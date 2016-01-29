#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Dump functions for MetaCast.
'''
import json
import datetime
from lxml import etree

from metacast import __version__
from metacast import utils
from metacast.models import MetaCast


# XML
# ----------------------------------------------------------------------------
def load_xml_bytes(xml_bytes):
    root = etree.fromstring(xml_bytes)
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
    for element in videos:
        for attr in element.attrib:
            element.attrib['is_%s' % attr] = element.attrib[attr]
        if element.tag == 'publishid' and element.get('type'):
            element.set('service', element.get('type'))
    # load from xml
    mc = MetaCast.from_xml(root)
    return mc


def dump_xml_bytes(mc):
    data = mc.to_xml()
    data.set('version', __version__)
    doc = etree.ElementTree(data)
    return etree.tostring(doc, pretty_print=True, xml_declaration=True, encoding='utf-8')


def load_xml(fileobj):
    data = fileobj.read()
    return load_xml_bytes(data)


def dump_xml(mc, fileobj):
    data = dump_xml_bytes(mc)
    fileobj.write(data)


# JSON
# ----------------------------------------------------------------------------
def load_json_str(json_str):
    data = json.loads(json_str)
    mc = MetaCast.from_json(data)
    return mc


def dump_json_str(mc, pretty=True):
    data = mc.to_json()
    data['version'] = __version__
    if pretty:
        data = json.dumps(data, sort_keys=True, indent=4)
    else:
        data = json.dumps(data)
    return data


def load_json(fileobj):
    data = fileobj.read().decode('utf-8')
    return load_json_str(data)


def dump_json(mc, fileobj):
    data = dump_json_str(mc)
    fileobj.write(data.encode('utf-8'))


# JS
# ----------------------------------------------------------------------------
JS_HEADER = '''/* MetaCast - v%s */
/* https://github.com/UbiCastTeam/metacast */''' % __version__


def load_js(fileobj):
    js_str = fileobj.read().decode('utf-8')
    to_find = 'var metadata = '
    start = js_str.find(to_find)
    if start == -1:
        raise Exception('Invalid file: metadata variable not found.')
    json_str = js_str[start + len(to_find):]
    if json_str.endswith(';'):
        json_str = json_str[:-1]
    return load_json_str(json_str)


def dump_js(mc, fileobj):
    data = dump_json_str(mc)
    data = JS_HEADER + '\nvar metadata = ' + data + ';'
    fileobj.write(data.encode('utf-8'))


# Dynamic
# ----------------------------------------------------------------------------
def load(path):
    if path.endswith('xml'):
        load_fct = load_xml
    elif path.endswith('json'):
        load_fct = load_json
    elif path.endswith('js'):
        load_fct = load_js
    else:
        raise Exception('Invalid file extension.')
    with open(path, 'rb') as fileobj:
        mc = load_fct(fileobj)
    return mc


def dump(mc, path):
    if path.endswith('xml'):
        dump_fct = dump_xml
    elif path.endswith('json'):
        dump_fct = dump_json
    elif path.endswith('js'):
        dump_fct = dump_js
    else:
        raise Exception('Invalid file extension.')
    with open(path, 'wb') as fileobj:
        dump_fct(mc, fileobj)
