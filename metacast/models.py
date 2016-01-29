#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Models for MetaCast.
'''
from __future__ import print_function
from metacast import structure as st
from metacast import utils


class Profile(st.BaseModel):
    name = st.TextField(is_repr=True)
    label = st.TextField()
    cost = st.IntegerField()
    recipe = st.JSONField()


class Output(st.BaseModel):
    name = st.TextField(is_repr=True)
    type = st.TextField(is_repr=True)
    width = st.IntegerField()
    height = st.IntegerField()
    profile = st.OneModelField(model=Profile)


class Transcoding(st.BaseModel):
    service = st.TextField(is_repr=True, xml_attr=True)
    outputs = st.ManyModelField(model=Output)


class PublishId(st.BaseModel):
    service = st.TextField(is_repr=True, xml_inner=True)
    name = st.TextField(is_repr=True, xml_attr=True)


class Video(st.BaseModel):
    filename = st.TextField(is_repr=True)
    file_hash = st.TextField()
    is_original = st.BooleanField(is_repr=True, xml_attr=True)
    is_main = st.BooleanField(is_repr=True, xml_attr=True)
    is_edited = st.BooleanField(is_repr=True, xml_attr=True)
    is_web2pod = st.BooleanField(xml_attr=True)
    is_autocam = st.BooleanField(xml_attr=True)
    is_archive = st.BooleanField(xml_attr=True)
    is_vga = st.BooleanField(xml_attr=True)
    used_for_export = st.BooleanField(xml_attr=True)
    source_hash = st.TextField()
    logo_hash = st.TextField()
    logo_position = st.TextField()
    duration = st.IntegerField()  # an integer in milliseconds (ms)
    width = st.IntegerField()
    height = st.IntegerField()
    creation_date = st.DatetimeField()
    info = st.TextField()
    publish_ids = st.ManyModelField(model=PublishId, xml_inner=True)
    transcodings = st.ManyModelField(model=Transcoding, xml_inner=True)


class Resource(st.BaseModel):
    service = st.TextField(is_repr=True)
    filename = st.TextField(is_repr=True)
    server = st.TextField()
    quality = st.TextField()
    downloadable = st.BooleanField(xml_attr=True)
    displayable = st.BooleanField(xml_attr=True)


class Tag(st.BaseModel):
    type = st.TextField(is_repr=True, xml_attr=True)
    content = st.TextField()


class Index(st.BaseModel):
    time = st.IntegerField(is_repr=True)  # time is an integer in milliseconds (ms)
    title = st.TextField(is_repr=True)
    description = st.TextField()
    image = st.TextField(is_repr=True)
    keywords = st.ListField()
    tags = st.ManyModelField(model=Tag, is_repr=True)

    def get_time(self):
        return self.time

    def get_time_in_seconds(self):
        return int(round(self.time / 1000.))

    def set_time(self, milliseconds):
        self.time = int(milliseconds)

    def set_time_in_seconds(self, seconds):
        self.time = int(seconds * 1000)

    def set_time_from_timecode(self, timecode):
        if len(timecode == 3):
            h, m, s = timecode
            ms = 0
        else:  # length is supposed to be 4
            h, m, s, ms = timecode
        self.time = 1000 * (h * 3600 + m * 60 + s) + ms

    def set_time_from_timecode_string(self, timecode_string):
        self.time = utils.get_time_from_timecode(timecode_string)

    def get_timecode_string(self, include_ms=True):
        if include_ms:
            return '%02d:%02d:%02d.%03d' % utils.get_timecode_from_time(self.time, include_ms)
        else:
            return '%02d:%02d:%02d' % utils.get_timecode_from_time(self.time, include_ms)

    def set_tags(self, tags):
        self.tags = list(tags) if tags else list()

    def __hash__(self):
        return self.time


class Attachment(st.BaseModel):
    order = st.IntegerField(is_repr=True)
    filename = st.TextField(is_repr=True)
    filesize = st.IntegerField()
    title = st.TextField(is_repr=True)
    description = st.TextField()
    keywords = st.ListField()


class Photo(Attachment):
    pass  # same fields as attachment


class Speaker(st.BaseModel):
    name = st.TextField(is_repr=True, xml_inner=True)
    email = st.TextField(is_repr=True, xml_attr=True)
    identifier = st.TextField(is_repr=True, xml_attr=True)


class Company(st.BaseModel):
    name = st.TextField(is_repr=True, xml_inner=True)
    url = st.TextField(is_repr=True, xml_attr=True)


class License(st.BaseModel):
    name = st.TextField(is_repr=True, xml_inner=True)
    url = st.TextField(is_repr=True, xml_attr=True)


class MetaCast(st.BaseModel):
    TYPE_VIDEO = 'video'
    TYPE_CHAPTERED = 'chaptered'
    TYPE_WEBINAR = 'webinar'
    TYPE_DUAL = 'dual'
    METACAST_TYPES = (TYPE_VIDEO, TYPE_CHAPTERED, TYPE_WEBINAR, TYPE_DUAL)

    TYPE_URL = 'url'
    TYPE_BOTR = 'botr'
    TYPE_RAMBLA = 'rambla'
    PUBLISH_TYPES = (TYPE_URL, TYPE_BOTR, TYPE_RAMBLA)

    layout = st.TextField(is_repr=True, xml_attr=True)
    owner = st.TextField(xml_attr=True)
    language = st.TextField(is_repr=True, xml_attr=True)
    title = st.TextField(is_repr=True)
    description = st.TextField()
    speaker = st.OneModelField(model=Speaker, xml_inner=True)
    company = st.OneModelField(model=Company, xml_inner=True)
    license = st.OneModelField(model=License, xml_inner=True)
    location = st.TextField()
    category = st.TextField()
    creation = st.DatetimeField()
    keywords = st.ListField()
    indexes = st.ManyModelField(model=Index)
    videos = st.ManyModelField(model=Video)
    resources = st.ManyModelField(model=Resource)
    attachments = st.ManyModelField(model=Attachment)
    photos = st.ManyModelField(model=Photo)
    data = st.JSONField()

    def sort_indexes(self, attr_key='time'):
        self.indexes.sort(key=lambda x: getattr(x, attr_key))
