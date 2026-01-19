import datetime

import pytest

from metacast import models


@pytest.fixture()
def mc():
    mc = models.MetaCast(title='test', layout='video', creation=datetime.datetime.now(), owner='ABéêèàùöû')
    mc.speaker = models.Speaker()
    mc.license = models.License(name='test', url='http://test')
    mc.data = {"scorm": "2004"}
    mc.tag_types = [
        models.TagType(
            slug='question',
            categories=[models.TagTypeCategory(slug='imlost')])
    ]
    mc.indexes = [
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
    mc.videos = [
        models.Video(filename='media', publish_ids=[
            models.PublishId(service='amazon', name='test')
        ], transcoding=models.Transcoding(
            service='zencoder', outputs=[
                models.Output(name='video_high.mp4', type='hd_video', width=None, height=720, profile=models.Profile(
                    name='mp4_hd_ready',
                    label='MP4 HD ready',
                    cost=2.0,
                    recipe=dict(
                        audio_quality=3, keyframe_interval=25, hint=True, height=720, audio_normalize=True,
                        audio_codec='aac', video_codec='h264', quality=4
                    )
                ))
            ])
        )
    ]
    return mc
