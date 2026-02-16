'''
Dump functions for MetaCast.
'''
import datetime
import json
import re
from xml.etree import ElementTree
from pathlib import Path

from metacast import __version__
from metacast.models import MetaCast


def _add_text_node(parent, name, node):
    if node is None or not node.text:
        return
    sub = ElementTree.Element(name)
    sub.text = node.text
    parent.append(sub)
    return sub


def _convert_timecode(timecode):
    time_val = 0
    parts = timecode.split(':')
    if part := parts.pop():
        time_val += 1000 * int(part)
    if part := parts.pop():
        time_val += 1000 * 60 * int(part)
    if part := parts.pop():
        time_val += 1000 * 3600 * int(part)
    return time_val


def _convert_old_date(date_string):
    try:
        dt = datetime.datetime.strptime(date_string, '%a %b %d %H:%M:%S %Y')
    except ValueError:
        return None
    else:
        return dt.strftime('%Y-%m-%d %H:%M:%S')


def load_xml(content):
    root = ElementTree.fromstring(content)

    # Get version
    version = root.get('version')
    if not version or not re.match(r'\d+\.\d+', version):
        raise ValueError('Invalid file content: metadata version not found.')
    version = tuple(int(val) for val in version.split('.'))

    # Apply compatibility changes to data
    if version < (2, 6):
        # Replace chapters tags with index
        chapters = root.find('chapters')
        if chapters is not None:
            chapters.tag = 'indexes'
            for element in chapters:
                if element.tag == 'item':
                    element.tag = 'index'
                node = element.find('timecode')
                if node is not None:
                    node.tag = 'time'
                    node.text = str(_convert_timecode(node.text))
    if version < (3, 0):
        # Rename type into layout
        if root.get('type'):
            root.set('layout', root.get('type'))
        # Change date format
        creation = root.find('creation')
        if creation is not None and creation.text:
            if new_dt := _convert_old_date(creation.text):
                creation.text = new_dt
        # Replace speaker identifier
        speaker = root.find('speaker')
        if speaker is not None and speaker.get('id'):
            speaker.set('identifier', speaker.get('id'))
        # Rename indexes description to content
        indexes = root.find('indexes')
        if indexes is not None:
            for element in indexes:
                node = element.find('description')
                if node is not None:
                    node.tag = 'content'
    if version < (4, 0):
        # Migrate "category" to "channel"
        category = root.find('category')
        if category is not None:
            category.tag = 'channel'
        # Set indexes "attachment" values from "image" values and migrate tags
        indexes = root.find('indexes')
        if indexes is not None:
            for element in indexes:
                for node_image in element.findall('./image'):
                    node_image.tag = 'attachment'
                    if node_image.text:
                        node_image.text = 'images/' + node_image.text
                for node_tags in element.findall('./tags'):
                    tag_type = []
                    tag_category = []
                    for node_tag in node_tags:
                        if node_tag.get('type'):
                            tag_type.append(node_tag.get('type'))
                        for node_content in node_tag.findall('./content'):
                            node_content.tag = 'data'
                            node_tag.remove(node_content)
                            element.append(node_content)
                        for node_slug in node_tag.findall('./category/tagtypecategory/slug'):
                            if node_slug.text:
                                tag_category.append(node_slug.text)
                    if tag_type or tag_category:
                        sub = ElementTree.Element('tag')
                        sub.text = ('/'.join(tag_type) + ':' + '/'.join(tag_category)).strip(' :')
                        element.append(sub)
        # Set photos "attachment" values from "filename" values
        photos = root.find('photos')
        if photos is not None:
            for element in photos:
                node = element.find('filename')
                if node is not None:
                    node.tag = 'attachment'
                    if node.text:
                        node.text = 'photos/' + node.text
        # Set resources "uri" values from "filename" and "server" values
        resources = root.find('resources')
        if resources is not None:
            for node_video in resources:
                uri = ''
                for node_name in ('server', 'filename'):
                    node = node_video.find(node_name)
                    if node is not None:
                        if node.text:
                            uri += node.text
                        node_video.remove(node)
                if uri:
                    node_video.text = uri
        # Migrate attachments
        subtitles = root.find('subtitles')
        attachments = root.find('attachments')
        if attachments is not None:
            for element in attachments:
                node = element.find('filename')
                filename = node.text if node is not None else ''
                if not filename:
                    continue
                if filename.startswith('subtitles/'):
                    if subtitles is None:
                        subtitles = ElementTree.Element('subtitles')
                        root.append(subtitles)
                    node = ElementTree.Element('subtitle')
                    _add_text_node(node, 'attachment', element.find('filename'))
                    _add_text_node(node, 'label', element.find('title'))
                    _add_text_node(node, 'language', element.find('description'))
                    sub = _add_text_node(node, 'visible', element.find('order'))
                    if sub is not None:
                        sub.text = '1' if sub.text == '1' else '0'
                    subtitles.append(node)
                elif filename.startswith('playersettings/'):
                    if resources is None:
                        resources = ElementTree.Element('resources')
                        root.append(resources)
                    node = ElementTree.Element('resource')
                    node.set('service', 'player')
                    sub = element.find('filename')
                    if sub is not None and sub.text:
                        node.text = sub.text
                    sub = element.find('title')
                    if sub is not None and sub.text:
                        if 'logo' in sub.text:
                            node.set('name', 'logo')
                        if 'background' in sub.text:
                            node.set('name', 'background')
                    resources.append(node)
                else:
                    if indexes is None:
                        indexes = ElementTree.Element('indexes')
                        root.append(indexes)
                    node = ElementTree.Element('index')
                    _add_text_node(node, 'attachment', element.find('filename'))
                    _add_text_node(node, 'title', element.find('title'))
                    _add_text_node(node, 'content', element.find('description'))
                    _add_text_node(node, 'keywords', element.find('keywords'))
                    indexes.append(node)
            root.remove(attachments)
        # Migrate videos to resources
        videos = root.find('videos')
        transcoding_service = None
        if videos is not None:
            for node_video in videos:
                for node in node_video.findall('./publishid'):
                    service = node.get('service') or node.get('type')
                    uri = node.text
                    if not service or not uri:
                        continue
                    if resources is None:
                        resources = ElementTree.Element('resources')
                        root.append(resources)
                    node = ElementTree.Element('resource')
                    node.set('service', service)
                    node.text = uri
                    resources.append(node)
                for node in node_video.findall('./transcoding'):
                    if node.get('service'):
                        transcoding_service = node.get('service')
        if transcoding_service:
            markers = root.find('markers')
            if markers is None:
                markers = ElementTree.Element('markers')
                root.append(markers)
            if markers.text:
                markers.text = f'{markers.text},transcoding:{transcoding_service}'
            else:
                markers.text = f'transcoding:{transcoding_service}'

    # Load from xml
    mc = MetaCast.from_xml(root)
    mc.source_version = version
    mc.source_format = 'xml'
    mc.sort_indexes()
    return mc


def dump_xml(mc):
    data = mc.to_xml()
    data.set('version', __version__)
    ElementTree.indent(data)
    content = '<?xml version="1.0" encoding="utf-8"?>\n'
    # The XML declaration is manually added to use double quotes
    content += ElementTree.tostring(data, xml_declaration=False, encoding='unicode')
    return content


def load_json(content):
    data = json.loads(content)

    # Get version
    version = data.get('version')
    if not version or not re.match(r'\d+\.\d+', version):
        raise ValueError('Invalid file content: metadata version not found.')
    version = tuple(int(val) for val in version.split('.'))

    # Apply compatibility changes to data
    if version < (2, 6):
        # Replace chapters tags with index
        if data.get('chapters'):
            data['indexes'] = data.pop('chapters')
        # Convert timecode to time
        for item in data.get('indexes', []):
            if timecode := item.pop('timecode', None):
                item['time'] = _convert_timecode(timecode)
    if version < (3, 0):
        # Rename type into layout
        if data.get('type'):
            data['layout'] = data.pop('type')
        # Change date format
        if data.get('creation'):
            if new_dt := _convert_old_date(data['creation']):
                data['creation'] = new_dt
        # Replace speaker identifier
        speaker = data.get('speaker')
        if speaker is not None and speaker.get('id'):
            speaker['identifier'] = speaker.get('id')
        # Rename indexes description to content
        for item in data.get('indexes', []):
            if description := item.pop('description', None):
                item['content'] = description
    if version < (4, 0):
        # Migrate "category" to "channel"
        if 'category' in data:
            data['channel'] = data.pop('category')
        # Set indexes "attachment" values from "image" values and migrate tags
        for item in data.get('indexes', []):
            if name := item.pop('image', None):
                item['attachment'] = 'images/' + name
            if tags := item.pop('tags', None):
                tag_type = []
                tag_category = []
                for tag in tags:
                    if tag.get('content'):
                        item.setdefault('data', '')
                        item['data'] += tag['content']
                    if slug := tag.get('type'):
                        tag_type.append(slug)
                    if slug := tag.get('category', {}).get('slug'):
                        tag_category.append(slug)
                if tag_type or tag_category:
                    item['tag'] = ('/'.join(tag_type) + ':' + '/'.join(tag_category)).strip(' :')
        # Set resources "uri" values from "filename" and "server" values
        for item in data.get('resources', []):
            uri = item.pop('server', '') + item.pop('filename', '')
            if uri:
                item['uri'] = uri
        # Set photos "attachment" values from "filename" values
        for item in data.get('photos', []):
            if name := item.pop('filename', None):
                item['attachment'] = 'photos/' + name
        # Migrate attachments
        for item in data.pop('attachments', []):
            filename = item.get('filename', '')
            if not filename:
                continue
            if filename.startswith('subtitles/'):
                data.setdefault('subtitles', []).append({
                    'attachment': filename,
                    'label': item.get('title', ''),
                    'language': item.get('description', ''),
                    'visible': item.get('order') == 1,
                })
            elif filename.startswith('playersettings/'):
                data.setdefault('resources', []).append({
                    'service': 'player',
                    'name': 'logo' if 'logo' in item.get('title', '') else 'background',
                    'uri': filename,
                })
            else:
                data.setdefault('indexes', []).append({
                    'attachment': filename,
                    'title': item.get('title', ''),
                    'content': item.get('description', ''),
                    'keywords': item.get('keywords', ''),
                })
        # Migrate videos
        transcoding_service = None
        for item in data.pop('videos', []):
            for publish_id in item.get('publish_ids', []):
                if not publish_id.get('service') and not publish_id.get('name'):
                    continue
                data.setdefault('resources', []).append({
                    'service': publish_id.get('service', ''),
                    'uri': publish_id.get('name', ''),
                })
            if tr_val := item.get('transcoding', {}).get('service'):
                transcoding_service = tr_val
        if transcoding_service:
            if data.get('markers'):
                data['markers'] += f',transcoding:{transcoding_service}'
            else:
                data['markers'] = f'transcoding:{transcoding_service}'

    # Load from json
    mc = MetaCast.from_json(data)
    mc.source_version = version
    mc.source_format = 'json'
    mc.sort_indexes()
    return mc


def dump_json(mc):
    data = mc.to_json()
    data['version'] = __version__
    content = json.dumps(data, sort_keys=True, indent=4)
    return content


JS_HEADER = '''/* MetaCast - v%s */
/* https://github.com/UbiCastTeam/metacast */''' % __version__


def load_js(content):
    to_find = 'var metadata = '
    start = content.find(to_find)
    if start == -1:
        raise ValueError('Invalid file content: metadata variable not found.')
    json_content = content[start + len(to_find):]
    json_content = json_content.rstrip().rstrip(';')
    return load_json(json_content)


def dump_js(mc):
    content = dump_json(mc)
    return JS_HEADER + '\nvar metadata = ' + content + ';'


def load(path):
    if not isinstance(path, Path):
        path = Path(path)

    if path.name.endswith('xml'):
        load_fct = load_xml
    elif path.name.endswith('json'):
        load_fct = load_json
    elif path.name.endswith('js'):
        load_fct = load_js
    else:
        raise ValueError('Invalid path extension.')

    with open(path, 'r') as fileobj:
        content = fileobj.read()

    mc = load_fct(content)
    return mc


def load_file(fileobj):
    content = fileobj.read()

    if content.startswith('<'):
        load_fct = load_xml
    elif content.startswith('{'):
        load_fct = load_json
    elif content.startswith('/'):
        load_fct = load_js
    else:
        raise ValueError('Invalid file content.')

    mc = load_fct(content)
    return mc


def dump(mc, path):
    if not isinstance(path, Path):
        path = Path(path)

    if path.name.endswith('xml'):
        dump_fct = dump_xml
    elif path.name.endswith('json'):
        dump_fct = dump_json
    elif path.name.endswith('js'):
        dump_fct = dump_js
    else:
        raise ValueError('Invalid path extension.')

    with open(path, 'w') as fileobj:
        fileobj.write(dump_fct(mc))


def dump_file(mc, fileobj):
    if fileobj.name.endswith('xml'):
        dump_fct = dump_xml
    elif fileobj.name.endswith('json'):
        dump_fct = dump_json
    elif fileobj.name.endswith('js'):
        dump_fct = dump_js
    else:
        raise ValueError('Invalid file extension.')

    fileobj.write(dump_fct(mc))
