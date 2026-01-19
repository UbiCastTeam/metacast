from metacast import models


def test_indexes(mc):
    assert len(mc.indexes) == 3

    assert mc.indexes[0].time == 0
    assert mc.indexes[0].get_timecode_string() == '00:00:00.000'
    assert mc.indexes[0].get_timecode_string(include_ms=False) == '00:00:00'
    assert len(mc.indexes[0].tags) == 0

    assert mc.indexes[1].time == 452
    assert mc.indexes[1].get_timecode_string() == '00:00:00.452'
    assert mc.indexes[1].get_timecode_string(include_ms=False) == '00:00:00'
    assert len(mc.indexes[1].tags) == 1
    assert mc.indexes[1].tags[0].type == 'pre-start'

    assert mc.indexes[2].time == 9_000
    assert mc.indexes[2].get_timecode_string() == '00:00:09.000'
    assert mc.indexes[2].get_timecode_string(include_ms=False) == '00:00:09'
    assert len(mc.indexes[2].tags) == 1
    assert mc.indexes[2].tags[0].type == 'question'

    current = list(mc.indexes)
    mc.sort_indexes()
    assert mc.indexes == current


def test_new_index():
    new_index = models.Index()
    new_index.set_time_from_timecode_string('00:06:03.050')
    assert new_index.time == 363_050
    assert new_index.get_time() == 363_050
    assert new_index.get_time_in_seconds() == 363
    assert new_index.__hash__() == 363_050

    new_index.set_time_from_timecode((0, 6, 3, 50))
    assert new_index.time == 363_050

    new_index.set_time_from_timecode((1, 2, 20))
    assert new_index.time == 3_740_000

    new_index.set_time(20)
    assert new_index.time == 20

    new_index.set_time_in_seconds(1)
    assert new_index.time == 1_000

    new_tag = models.Tag(type='my-tag')
    new_index.set_tags([new_tag])
    assert len(new_index.tags) == 1
    assert new_index.tags[0].type == 'my-tag'
