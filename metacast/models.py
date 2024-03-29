#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Models for MetaCast.
'''
from metacast import structure as st
from metacast import utils


class Profile(st.BaseModel):
    name = st.TextField(is_repr=True)
    label = st.TextField()
    cost = st.FloatField()
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
    service = st.TextField(is_repr=True, xml_attr=True)
    name = st.TextField(is_repr=True, xml_inner=True)


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
    transcoding = st.OneModelField(model=Transcoding, xml_inner=True)


class Resource(st.BaseModel):
    service = st.TextField(is_repr=True, xml_attr=True)
    filename = st.TextField(is_repr=True)
    server = st.TextField()
    quality = st.TextField(xml_attr=True)
    downloadable = st.BooleanField(xml_attr=True)
    displayable = st.BooleanField(xml_attr=True)


class TagTypeCategory(st.BaseModel):
    '''
        Represent a type category
        - slug:
            used to detect if type already exists or needs to be created
        - label:
            type label like More information
        - visibility:
            if type is public or private
        - enable_social:
            enable social features like response, vote, ect...
        - enable_mailing:
            enable mailing if users are following the annotation timeline
        - enable_notification:
            enable in player notification if the sidebar is closed
    '''
    slug = st.TextField(is_repr=True)
    label = st.TextField()
    enable_mailing = st.BooleanField()
    enable_notification = st.BooleanField()


class TagType(st.BaseModel):
    '''
        Represent a tag type(slide, chapter, ect...)
        - internal_type:
            for particular tags (slide, chapter, activity)
        - slug:
            used to detect if type already exists or needs to be created
        - label:
            type label like Slide
        - color:
            type color representation
        - visibility:
            if type is public or private
        - allow_title:
            allow a title for the annotation
        - allow_content:
            allow a description for the annotation
        - allow_attachment:
            allow an attachment for the annotation
        - allow_keywords:
            allow keywords for the annotation
        - enable_social:
            enable social features like response, vote, ect...
        - enable_mailing:
            enable mailing if users are following the annotation timeline
        - enable_notification:
            enable in player notification if the sidebar is closed
    '''
    internal_type = st.TextField(is_repr=True)
    slug = st.TextField(is_repr=True)
    label = st.TextField()
    color = st.TextField()
    visibility = st.BooleanField()
    editorial = st.BooleanField()
    allow_title = st.BooleanField()
    allow_content = st.BooleanField()
    allow_attachment = st.BooleanField()
    allow_keywords = st.BooleanField()
    enable_social = st.BooleanField()
    enable_mailing = st.BooleanField()
    enable_notification = st.BooleanField()
    categories = st.ManyModelField(model=TagTypeCategory)


class Tag(st.BaseModel):
    '''
        Represent an annotation for mediaserver
        or an action point for easycast
        - type:
            the slug of a TagType for mediaserver
            or an internal tag type for easycast
        - content:
            a json for mediaserver that represent an annotation
            or an internal value for easycast
    '''
    type = st.TextField(is_repr=True, xml_attr=True)
    category = st.OneModelField(model=TagTypeCategory)
    content = st.TextField()


class Index(st.BaseModel):
    '''
        Represent an index in the video timeline
        - time:
            time is an integer in milliseconds (ms)
        - title:
            used by easycast and offline player to precise a chapters
        - description:
            used by easycast and offline player to precise the content of slides and chapters
        - image:
            used by easycast and offline player to give the slides path
        - keywords:
            used by easycast and offline player to precise keywords for chapters and slides
        - tags:
            used by easycast for adding internal actions
            and used by mediaserver to declare annotations
    '''
    time = st.IntegerField(is_repr=True)
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
    path = st.TextField()
    location = st.TextField()
    category = st.TextField()
    creation = st.DatetimeField()
    keywords = st.ListField()
    tag_types = st.ManyModelField(model=TagType)
    indexes = st.ManyModelField(model=Index)
    videos = st.ManyModelField(model=Video)
    resources = st.ManyModelField(model=Resource)
    attachments = st.ManyModelField(model=Attachment)
    photos = st.ManyModelField(model=Photo)
    data = st.JSONField()

    def sort_indexes(self, attr_key='time'):
        self.indexes.sort(key=lambda x: getattr(x, attr_key))
