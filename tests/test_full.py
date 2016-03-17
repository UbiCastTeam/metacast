#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
MetaCast - Test of import/export functions.
'''
from __future__ import print_function
import datetime
import unittest
import tempfile
try:
    from StringIO import BytesIO
except ImportError:
    # Python 3
    from io import BytesIO

from metacast import models
from metacast.io import load_xml, dump_xml, load_json, dump_json, load_js, dump_js

XML_RESULT = '''<?xml version='1.0' encoding='utf-8'?>
<metacast layout="video" version="3.0">
  <creation>%s</creation>
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
        <tag type="slide">
          <content>{ "label": "Slide 1", "type": { "slug": "slide" }}</content>
        </tag>
      </tags>
    </index>
  </indexes>
  <tag_types>
    <tagtype>
      <internal_type>slide</internal_type>
      <slug>slide</slug>
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

JSON_RESULT_PYTHON2 = '''{
    "creation": "%s", 
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
                    "content": "{ \\"label\\": \\"Slide 1\\", \\"type\\": { \\"slug\\": \\"slide\\" }}", 
                    "type": "slide"
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
    "tag_types": [
        {
            "internal_type": "slide", 
            "slug": "slide"
        }
    ], 
    "title": "test", 
    "version": "3.0", 
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
JSON_RESULT_PYTHON3 = '''{
    "creation": "%s",
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
                    "content": "{ \\"label\\": \\"Slide 1\\", \\"type\\": { \\"slug\\": \\"slide\\" }}",
                    "type": "slide"
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
    "tag_types": [
        {
            "internal_type": "slide",
            "slug": "slide"
        }
    ],
    "title": "test",
    "version": "3.0",
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

JS_RESULT_PYTHON2 = '''/* MetaCast - v3.0 */
/* https://github.com/UbiCastTeam/metacast */
var metadata = {
    "creation": "%s", 
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
                    "content": "{ \\"label\\": \\"Slide 1\\", \\"type\\": { \\"slug\\": \\"slide\\" }}", 
                    "type": "slide"
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
    "tag_types": [
        {
            "internal_type": "slide", 
            "slug": "slide"
        }
    ], 
    "title": "test", 
    "version": "3.0", 
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

JS_RESULT_PYTHON3 = '''/* MetaCast - v3.0 */
/* https://github.com/UbiCastTeam/metacast */
var metadata = {
    "creation": "%s",
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
                    "content": "{ \\"label\\": \\"Slide 1\\", \\"type\\": { \\"slug\\": \\"slide\\" }}",
                    "type": "slide"
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
    "tag_types": [
        {
            "internal_type": "slide",
            "slug": "slide"
        }
    ],
    "title": "test",
    "version": "3.0",
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
        self.mc = models.MetaCast(title='test', layout='video', creation=datetime.datetime.now())
        self.mc.speaker = models.Speaker()
        self.mc.license = models.License(name='test', url='http://test')
        self.mc.tag_types = [models.TagType(internal_type='slide', slug='slide')]
        self.mc.indexes = [
            models.Index(time=0),
            models.Index(time=452, tags=[
                models.Tag(type='pre-start'),
            ]),
            models.Index(time=9000, tags=[
                models.Tag(type='slide', content='{ "label": "Slide 1", "type": { "slug": "slide" }}'),
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
        buf = BytesIO()
        dump_xml(self.mc, buf)
        result = buf.getvalue().decode('utf-8')
        self.assertEqual(XML_RESULT % self.mc.creation.strftime('%Y-%m-%d %H:%M:%S'), result)

    def test_dump_json(self):
        buf = BytesIO()
        dump_json(self.mc, buf)
        result = buf.getvalue().decode('utf-8')
        try:
            JSON_RESULT = unicode(JSON_RESULT_PYTHON2)  # python 2 add space at the end offlines
        except NameError:
            JSON_RESULT = JSON_RESULT_PYTHON3
        self.assertEqual(JSON_RESULT % self.mc.creation.strftime('%Y-%m-%d %H:%M:%S'), result)

    def test_dump_js(self):
        buf = BytesIO()
        dump_js(self.mc, buf)
        result = buf.getvalue().decode('utf-8')
        try:
            JS_RESULT = unicode(JS_RESULT_PYTHON2)  # python 2 add space at the end offlines
        except NameError:
            JS_RESULT = JS_RESULT_PYTHON3
        self.assertEqual(JS_RESULT % self.mc.creation.strftime('%Y-%m-%d %H:%M:%S'), result)

    def test_load_xml(self):
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8') as fp:
            fp.write(XML_RESULT % self.mc.creation.strftime('%Y-%m-%d %H:%M:%S'))
            fp.flush()
            path = fp.name
            with open(path, 'rb') as fpr:
                mc = load_xml(fpr)
                fpr.close()
            fp.close()
        self.assertIsInstance(mc, models.MetaCast)

    def test_load_json(self):
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8') as fp:
            fp.write(JSON_RESULT_PYTHON3 % self.mc.creation.strftime('%Y-%m-%d %H:%M:%S'))
            fp.flush()
            path = fp.name
            with open(path, 'rb') as fpr:
                mc = load_json(fpr)
                fpr.close()
            fp.close()
        self.assertIsInstance(mc, models.MetaCast)

    def test_load_js(self):
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8') as fp:
            fp.write(JS_RESULT_PYTHON3 % self.mc.creation.strftime('%Y-%m-%d %H:%M:%S'))
            fp.flush()
            path = fp.name
            with open(path, 'rb') as fpr:
                mc = load_js(fpr)
                fpr.close()
            fp.close()
        self.assertIsInstance(mc, models.MetaCast)

if __name__ == '__main__':
    unittest.main()
