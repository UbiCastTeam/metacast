'''
Dump functions for MetaCast.
'''
import json
import datetime
from xml.etree import ElementTree
from pathlib import Path

from metacast import __version__
from metacast import utils
from metacast.models import MetaCast


def load_xml(content):
    root = ElementTree.fromstring(content)
    # apply compatibility changes to data
    # change layout (version < 3.0)
    if root.get('type'):
        root.set('layout', root.get('type'))
    # change date format (version < 3.0)
    creation = root.find('creation')
    if creation is not None and creation.text:
        try:
            date = datetime.datetime.strptime(creation.text, '%a %b %d %H:%M:%S %Y')
            creation.text = date.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            pass
    # replace speaker identifier
    speaker = root.find('speaker')
    if speaker is not None and speaker.get('id'):
        speaker.set('identifier', speaker.get('id'))
    # replace chapters tags with index (version < 2.6)
    chapters = root.find('chapters')
    if chapters is not None:
        chapters.tag = 'indexes'
        for element in chapters:
            if element.tag == 'item':
                element.tag = 'index'
                # convert timecode to time
                timecode = element.find('timecode')
                if timecode is not None:
                    timecode.tag = 'time'
                    timecode.text = str(utils.get_time_from_timecode(timecode.text))
    # set videos attributes names (version < 3.0)
    videos = root.find('videos')
    if videos is not None:
        for element in videos:
            for attr in list(element.attrib):
                element.set('is_%s' % attr, element.get(attr))
            for sub in element:
                if sub.tag == 'publishid' and sub.get('type'):
                    sub.set('service', sub.get('type'))
                elif sub.tag == 'creation_date' and sub.text:
                    try:
                        date = datetime.datetime.strptime(sub.text, '%a %b %d %H:%M:%S %Y')
                        sub.text = date.strftime('%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        pass
    # load from xml
    mc = MetaCast.from_xml(root)
    return mc


def dump_xml(mc):
    data = mc.to_xml()
    data.set('version', __version__)
    ElementTree.indent(data)
    return ElementTree.tostring(data, xml_declaration=True, encoding='unicode')


def load_json(content):
    data = json.loads(content)
    mc = MetaCast.from_json(data)
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
