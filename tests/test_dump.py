#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
MetaCast - Test of export function.
'''
from __future__ import print_function
import datetime
try:
    from StringIO import BytesIO
except ImportError:
    # Python 3
    from io import BytesIO

from metacast import models
from metacast.io import dump_xml, dump_json


if __name__ == '__main__':
    print('Creating MetaCast object')
    mc = models.MetaCast(title='test', layout='video', creation=datetime.datetime.now())
    mc.speaker = models.Speaker()
    mc.license = models.License(name='test', url='http://test')
    mc.indexes = [
        models.Index(time=0),
        models.Index(time=452, tags=[
            models.Tag(type='pre-start'),
        ]),
    ]
    mc.videos = [
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
    print(mc)
    print(mc.creation)

    print('Test xml export')
    print('----------------------------------------------')
    buf = BytesIO()
    dump_xml(mc, buf)
    result = buf.getvalue()
    print(result.decode('utf-8'))

    print('Test json export')
    print('----------------------------------------------')
    buf = BytesIO()
    dump_json(mc, buf)
    result = buf.getvalue()
    print(result.decode('utf-8'))
