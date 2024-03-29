#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
MetaCast - Test of import/export functions.
'''
from io import BytesIO
import datetime
import tempfile
import unittest

from metacast import __version__
from metacast import models
from metacast.io import load_xml, dump_xml, load_json, dump_json, load_js, dump_js

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
        <tag type="pre-start"/>
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
</metacast>
'''

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
}'''

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
};'''


class TestFull(unittest.TestCase):
    def setUp(self):
        self.mc = models.MetaCast(title='test', layout='video', creation=datetime.datetime.now(), owner='ABéêèàùöû')
        self.mc.speaker = models.Speaker()
        self.mc.license = models.License(name='test', url='http://test')
        self.mc.data = {"scorm": "2004"}
        self.mc.tag_types = [
            models.TagType(
                slug='question',
                categories=[models.TagTypeCategory(slug='imlost')])
        ]
        self.mc.indexes = [
            models.Index(time=0),
            models.Index(time=452, tags=[
                models.Tag(type='pre-start'),
            ]),
            models.Index(time=9000, tags=[
                models.Tag(
                    type='question',
                    content='{ "label": "Question 1", "type": { "slug": "question" }}',
                    category=models.TagTypeCategory(slug='imlost')
                ),
            ]),
        ]
        self.mc.videos = [
            models.Video(filename='media', publish_ids=[
                models.PublishId(service='amazon', name='test')
            ], transcoding=models.Transcoding(
                service='zencoder', outputs=[
                    models.Output(name='video_high.mp4', type='hd_video', width=None, height=720, profile=models.Profile(
                        name='mp4_hd_ready',
                        label='MP4 HD ready',
                        cost=2.0,
                        recipe=dict(audio_quality=3, keyframe_interval=25, hint=True, height=720, audio_normalize=True, audio_codec='aac', video_codec='h264', quality=4)
                    ))
                ])
            )
        ]

    def test_dump_xml(self):
        try:
            expected = unicode(XML_RESULT % dict(version=__version__, creation=self.mc.creation.strftime('%Y-%m-%d %H:%M:%S')), 'utf-8')
        except NameError:
            expected = XML_RESULT % dict(version=__version__, creation=self.mc.creation.strftime('%Y-%m-%d %H:%M:%S'))
        buf = BytesIO()
        dump_xml(self.mc, buf)
        result = buf.getvalue().decode('utf-8')
        self.assertEqual(expected, result)

    def test_dump_json(self):
        buf = BytesIO()
        dump_json(self.mc, buf)
        result = buf.getvalue().decode('utf-8')
        try:
            expected = unicode(JSON_RESULT.replace(',', ', '), 'utf-8')  # python 2 add space after comas even on line end
        except NameError:
            expected = JSON_RESULT
        self.assertEqual(expected % dict(version=__version__, creation=self.mc.creation.strftime('%Y-%m-%d %H:%M:%S')), result)

    def test_dump_js(self):
        buf = BytesIO()
        dump_js(self.mc, buf)
        result = buf.getvalue().decode('utf-8')
        try:
            expected = unicode(JS_RESULT.replace(',', ', '), 'utf-8')  # python 2 add space after comas even on line end
        except NameError:
            expected = JS_RESULT
        self.assertEqual(expected % dict(version=__version__, creation=self.mc.creation.strftime('%Y-%m-%d %H:%M:%S')), result)

    def test_load_xml(self):
        with tempfile.NamedTemporaryFile(mode='w') as fp:
            text = XML_RESULT % dict(version=__version__, creation=self.mc.creation.strftime('%Y-%m-%d %H:%M:%S'))
            fp.write(text)
            fp.flush()
            path = fp.name
            with open(path, 'rb') as fpr:
                mc = load_xml(fpr)
                fpr.close()
            fp.close()
        self.assertIsInstance(mc, models.MetaCast)

    def test_load_json(self):
        with tempfile.NamedTemporaryFile(mode='w') as fp:
            text = JSON_RESULT % dict(version=__version__, creation=self.mc.creation.strftime('%Y-%m-%d %H:%M:%S'))
            try:
                fp.write(text.encode('utf-8'))  # Python 2
            except TypeError:
                fp.write(text)
            fp.flush()
            path = fp.name
            with open(path, 'rb') as fpr:
                mc = load_json(fpr)
                fpr.close()
            fp.close()
        self.assertIsInstance(mc, models.MetaCast)

    def test_load_js(self):
        with tempfile.NamedTemporaryFile(mode='w') as fp:
            text = JS_RESULT % dict(version=__version__, creation=self.mc.creation.strftime('%Y-%m-%d %H:%M:%S'))
            try:
                fp.write(text.encode('utf-8'))  # Python 2
            except TypeError:
                fp.write(text)
            fp.flush()
            path = fp.name
            with open(path, 'rb') as fpr:
                mc = load_js(fpr)
                fpr.close()
            fp.close()
        self.assertIsInstance(mc, models.MetaCast)


if __name__ == '__main__':
    unittest.main()
