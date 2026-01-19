'''
MetaCast - Test of import/export functions.
'''
import datetime
import tempfile

import pytest

from metacast import __version__
from metacast import io as mcio
from metacast import models


XML_RESULT = '''<?xml version='1.0' encoding='utf-8'?>
<metacast layout="video" owner="ABéêèàùöû" version="%(version)s">
  <creation>%(creation)s</creation>
  <data>{"scorm": "2004"}</data>
  <title>test</title>
  <license url="http://test">test</license>
  <indexes>
    <index>
      <time>452</time>
      <tags>
        <tag type="pre-start" />
      </tags>
    </index>
    <index>
      <time>9000</time>
      <tags>
        <tag type="question">
          <content>{ "label": "Question 1", "type": { "slug": "question" }}</content>
          <category>
            <tagtypecategory>
              <slug>imlost</slug>
            </tagtypecategory>
          </category>
        </tag>
      </tags>
    </index>
  </indexes>
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
  <videos>
    <video>
      <filename>media</filename>
      <transcoding service="zencoder">
        <outputs>
          <output>
            <height>720</height>
            <name>video_high.mp4</name>
            <type>hd_video</type>
            <profile>
              <profile>
                <cost>2.0</cost>
                <label>MP4 HD ready</label>
                <name>mp4_hd_ready</name>
                <recipe>{"audio_codec": "aac", "audio_normalize": true, "audio_quality": 3, "height": 720, "hint": true, "keyframe_interval": 25, "quality": 4, "video_codec": "h264"}</recipe>
              </profile>
            </profile>
          </output>
        </outputs>
      </transcoding>
      <publishid service="amazon">test</publishid>
    </video>
  </videos>
</metacast>'''  # noqa

JSON_RESULT = '''{
    "creation": "%(creation)s",
    "data": "{\\"scorm\\": \\"2004\\"}",
    "indexes": [
        {
            "tags": [
                {
                    "type": "pre-start"
                }
            ],
            "time": 452
        },
        {
            "tags": [
                {
                    "category": {
                        "slug": "imlost"
                    },
                    "content": "{ \\"label\\": \\"Question 1\\", \\"type\\": { \\"slug\\": \\"question\\" }}",
                    "type": "question"
                }
            ],
            "time": 9000
        }
    ],
    "layout": "video",
    "license": {
        "name": "test",
        "url": "http://test"
    },
    "owner": "AB\\u00e9\\u00ea\\u00e8\\u00e0\\u00f9\\u00f6\\u00fb",
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
    "version": "%(version)s",
    "videos": [
        {
            "filename": "media",
            "publish_ids": [
                {
                    "name": "test",
                    "service": "amazon"
                }
            ],
            "transcoding": {
                "outputs": [
                    {
                        "height": 720,
                        "name": "video_high.mp4",
                        "profile": {
                            "cost": 2.0,
                            "label": "MP4 HD ready",
                            "name": "mp4_hd_ready",
                            "recipe": "{\\"audio_codec\\": \\"aac\\", \\"audio_normalize\\": true, \\"audio_quality\\": 3, \\"height\\": 720, \\"hint\\": true, \\"keyframe_interval\\": 25, \\"quality\\": 4, \\"video_codec\\": \\"h264\\"}"
                        },
                        "type": "hd_video"
                    }
                ],
                "service": "zencoder"
            }
        }
    ]
}'''  # noqa

JS_RESULT = '''/* MetaCast - v%(version)s */
/* https://github.com/UbiCastTeam/metacast */
var metadata = {
    "creation": "%(creation)s",
    "data": "{\\"scorm\\": \\"2004\\"}",
    "indexes": [
        {
            "tags": [
                {
                    "type": "pre-start"
                }
            ],
            "time": 452
        },
        {
            "tags": [
                {
                    "category": {
                        "slug": "imlost"
                    },
                    "content": "{ \\"label\\": \\"Question 1\\", \\"type\\": { \\"slug\\": \\"question\\" }}",
                    "type": "question"
                }
            ],
            "time": 9000
        }
    ],
    "layout": "video",
    "license": {
        "name": "test",
        "url": "http://test"
    },
    "owner": "AB\\u00e9\\u00ea\\u00e8\\u00e0\\u00f9\\u00f6\\u00fb",
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
    "version": "%(version)s",
    "videos": [
        {
            "filename": "media",
            "publish_ids": [
                {
                    "name": "test",
                    "service": "amazon"
                }
            ],
            "transcoding": {
                "outputs": [
                    {
                        "height": 720,
                        "name": "video_high.mp4",
                        "profile": {
                            "cost": 2.0,
                            "label": "MP4 HD ready",
                            "name": "mp4_hd_ready",
                            "recipe": "{\\"audio_codec\\": \\"aac\\", \\"audio_normalize\\": true, \\"audio_quality\\": 3, \\"height\\": 720, \\"hint\\": true, \\"keyframe_interval\\": 25, \\"quality\\": 4, \\"video_codec\\": \\"h264\\"}"
                        },
                        "type": "hd_video"
                    }
                ],
                "service": "zencoder"
            }
        }
    ]
};'''  # noqa


def test_dump_xml(mc):
    expected = XML_RESULT % dict(version=__version__, creation=mc.creation.strftime('%Y-%m-%d %H:%M:%S'))
    result = mcio.dump_xml(mc)
    assert expected == result


def test_dump_json(mc):
    result = mcio.dump_json(mc)
    expected = JSON_RESULT
    assert expected % dict(version=__version__, creation=mc.creation.strftime('%Y-%m-%d %H:%M:%S')) == result


def test_dump_js(mc):
    result = mcio.dump_js(mc)
    expected = JS_RESULT
    assert expected % dict(version=__version__, creation=mc.creation.strftime('%Y-%m-%d %H:%M:%S')) == result


def test_load_xml():
    dt = datetime.datetime.now()
    with tempfile.NamedTemporaryFile(mode='w') as fp:
        text = XML_RESULT % dict(version=__version__, creation=dt.strftime('%Y-%m-%d %H:%M:%S'))
        fp.write(text)
        fp.flush()
        path = fp.name
        with open(path, 'r') as fo:
            content = fo.read()
    mc = mcio.load_xml(content)
    assert isinstance(mc, models.MetaCast)


def test_load_json():
    dt = datetime.datetime.now()
    with tempfile.NamedTemporaryFile(mode='w') as fp:
        text = JSON_RESULT % dict(version=__version__, creation=dt.strftime('%Y-%m-%d %H:%M:%S'))
        fp.write(text)
        fp.flush()
        path = fp.name
        with open(path, 'r') as fo:
            content = fo.read()
    mc = mcio.load_json(content)
    assert isinstance(mc, models.MetaCast)


def test_load_js():
    dt = datetime.datetime.now()
    with tempfile.NamedTemporaryFile(mode='w') as fp:
        text = JS_RESULT % dict(version=__version__, creation=dt.strftime('%Y-%m-%d %H:%M:%S'))
        fp.write(text)
        fp.flush()
        path = fp.name
        with open(path, 'r') as fo:
            content = fo.read()
    mc = mcio.load_js(content)
    assert isinstance(mc, models.MetaCast)


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
