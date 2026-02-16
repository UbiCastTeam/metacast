'''
MetaCast - Test of import/export functions.
'''
import datetime
import tempfile

import pytest

from metacast import __version__
from metacast import io as mcio
from metacast import models

PREVIOUS_VERION = '3.0'

XML_RESULT = '''<?xml version="1.0" encoding="utf-8"?>
<metacast layout="video" owner="ABéêèàùöû" version="%(version)s">
  <categories>course, online</categories>
  <creation>%(creation)s</creation>
  <data>{"opt": true, "scorm": "2004"}</data>
  <title>test</title>
  <license url="http://test">test</license>
  <indexes>
    <index>
      <tag>pre-start</tag>
      <time>452</time>
    </index>
    <index>
      <content>{"label": "Question 1", "poster": "Mr Test"}</content>
      <tag>question:imlost</tag>
      <time>9000</time>
    </index>
  </indexes>
  <resources>
    <resource downloadable="1" name="logo" quality="1920x1080" service="assets">file.png</resource>
  </resources>
  <tag_types>
    <tagtype>
      <slug>question</slug>
      <categories>
        <tagtypecategory>
          <slug>imlost</slug>
        </tagtypecategory>
      </categories>
    </tagtype>
  </tag_types>
</metacast>'''

JSON_RESULT = '''{
    "categories": [
        "course",
        "online"
    ],
    "creation": "%(creation)s",
    "data": {
        "opt": true,
        "scorm": "2004"
    },
    "indexes": [
        {
            "tag": "pre-start",
            "time": 452
        },
        {
            "content": "{\\"label\\": \\"Question 1\\", \\"poster\\": \\"Mr Test\\"}",
            "tag": "question:imlost",
            "time": 9000
        }
    ],
    "layout": "video",
    "license": {
        "name": "test",
        "url": "http://test"
    },
    "owner": "AB\\u00e9\\u00ea\\u00e8\\u00e0\\u00f9\\u00f6\\u00fb",
    "resources": [
        {
            "downloadable": true,
            "name": "logo",
            "quality": "1920x1080",
            "service": "assets",
            "uri": "file.png"
        }
    ],
    "tag_types": [
        {
            "categories": [
                {
                    "slug": "imlost"
                }
            ],
            "slug": "question"
        }
    ],
    "title": "test",
    "version": "%(version)s"
}'''

JS_RESULT = f'''/* MetaCast - v%(version)s */
/* https://github.com/UbiCastTeam/metacast */
var metadata = {JSON_RESULT};'''


def test_dump_xml(mc):
    expected = XML_RESULT % dict(version=__version__, creation=mc.creation.strftime('%Y-%m-%d %H:%M:%S'))
    result = mcio.dump_xml(mc)
    assert result == expected


def test_dump_json(mc):
    result = mcio.dump_json(mc)
    expected = JSON_RESULT
    assert result == expected % dict(version=__version__, creation=mc.creation.strftime('%Y-%m-%d %H:%M:%S'))


def test_dump_js(mc):
    result = mcio.dump_js(mc)
    expected = JS_RESULT
    assert result == expected % dict(version=__version__, creation=mc.creation.strftime('%Y-%m-%d %H:%M:%S'))


def test_load_xml():
    dt = datetime.datetime.now()
    with tempfile.NamedTemporaryFile(mode='w') as fp:
        text = XML_RESULT % dict(version=PREVIOUS_VERION, creation=dt.strftime('%Y-%m-%d %H:%M:%S'))
        fp.write(text)
        fp.flush()
        path = fp.name
        with open(path, 'r') as fo:
            content = fo.read()
    mc = mcio.load_xml(content)
    assert isinstance(mc, models.MetaCast)

    expected = XML_RESULT % dict(version=__version__, creation=mc.creation.strftime('%Y-%m-%d %H:%M:%S'))
    result = mcio.dump_xml(mc)
    assert result == expected


def test_load_json():
    dt = datetime.datetime.now()
    with tempfile.NamedTemporaryFile(mode='w') as fp:
        text = JSON_RESULT % dict(version=PREVIOUS_VERION, creation=dt.strftime('%Y-%m-%d %H:%M:%S'))
        fp.write(text)
        fp.flush()
        path = fp.name
        with open(path, 'r') as fo:
            content = fo.read()
    mc = mcio.load_json(content)
    assert isinstance(mc, models.MetaCast)

    result = mcio.dump_json(mc)
    expected = JSON_RESULT
    assert result == expected % dict(version=__version__, creation=mc.creation.strftime('%Y-%m-%d %H:%M:%S'))


def test_load_js():
    dt = datetime.datetime.now()
    with tempfile.NamedTemporaryFile(mode='w') as fp:
        text = JS_RESULT % dict(version=PREVIOUS_VERION, creation=dt.strftime('%Y-%m-%d %H:%M:%S'))
        fp.write(text)
        fp.flush()
        path = fp.name
        with open(path, 'r') as fo:
            content = fo.read()
    mc = mcio.load_js(content)
    assert isinstance(mc, models.MetaCast)

    result = mcio.dump_js(mc)
    expected = JS_RESULT
    assert result == expected % dict(version=__version__, creation=mc.creation.strftime('%Y-%m-%d %H:%M:%S'))


def test_dump(mc):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json') as fp:
        path = fp.name
        mcio.dump(mc, path)
        with open(path, 'r') as fo:
            content = fo.read()
    assert content == mcio.dump_json(mc)


def test_dump__invalid(mc):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.nope') as fp:
        path = fp.name
        with pytest.raises(ValueError):
            mcio.dump(mc, path)
