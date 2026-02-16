import datetime

import pytest

from metacast import models


@pytest.fixture()
def mc():
    mc = models.MetaCast(title='test', layout='video', creation=datetime.datetime.now(), owner='ABéêèàùöû')
    mc.speaker = models.Speaker()
    mc.license = models.License(name='test', url='http://test')
    mc.categories = ['course', 'online']
    mc.data = {"scorm": "2004", "opt": True}
    mc.tag_types = [
        models.TagType(slug='question', categories=[models.TagTypeCategory(slug='imlost')])
    ]
    mc.indexes = [
        models.Index(time=0),
        models.Index(time=452, tag='pre-start'),
        models.Index(time=9000, content='{"label": "Question 1", "poster": "Mr Test"}', tag='question:imlost')
    ]
    mc.resources = [
        models.Resource(service='assets', name='logo', uri='file.png', quality='1920x1080', downloadable=True)
    ]
    return mc
