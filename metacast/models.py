'''
Models for MetaCast.
'''
from metacast import structure as st


class TagTypeCategory(st.BaseModel):
    '''
    Represent a type category
    '''
    # The slug: a unique text containing only `a-z`, `0-9`, `_` and `-` (example: `important`)
    slug = st.TextField(is_repr=True)

    # The label (example: `Important`)
    label = st.TextField()

    # Indicates the order of appearance
    display_order = st.IntegerField()

    # Indicates if users can subscribe to mail notifications
    enable_mailing = st.BooleanField()

    # Indicates if indexes using this category should be notified in the player while playing
    enable_notification = st.BooleanField()


class TagType(st.BaseModel):
    '''
    Represent a tag type (slide, chapter, etc...)
    '''
    # The slug: a unique text containing only `a-z`, `0-9`, `_` and `-` (example: `slide`)
    slug = st.TextField(is_repr=True)

    # The label (example: `Slide`)
    label = st.TextField()

    # Indicates the order of appearance
    display_order = st.IntegerField()

    # The hexadecimal color code (example: `#123456`)
    color = st.TextField()

    # The visibility (enabled means public, disabled means private)
    visibility = st.BooleanField()

    # The editorial status
    editorial = st.BooleanField()

    # Indicates if a title can be set
    allow_title = st.BooleanField()

    # Indicates if a content can be set
    allow_content = st.BooleanField()

    # Indicates if an attachment can be set
    allow_attachment = st.BooleanField()

    # Indicates if keywords can be set
    allow_keywords = st.BooleanField()

    # Indicates if social interactions are allowed
    enable_social = st.BooleanField()

    # Indicates if users can subscribe to mail notifications
    enable_mailing = st.BooleanField()

    # Indicates if related indexes should be notified in the player while playing
    enable_notification = st.BooleanField()

    # The list of available categories for this type
    categories = st.ManyModelField(model=TagTypeCategory)


class Index(st.BaseModel):
    '''
    Represent an index in the timeline
    '''
    time = st.IntegerField(is_repr=True)  # Time in milliseconds (ms)
    title = st.TextField(is_repr=True)
    content = st.TextField()
    attachment = st.TextField(is_repr=True)  # The relative path (example: `images/slide.jpg`)
    keywords = st.ListField()
    tag = st.TextField(is_repr=True)  # The tag reference `<type_slug>:<category_slug>` (example: `note:important`)
    data = st.JSONField()  # Additional data


class Resource(st.BaseModel):
    service = st.TextField(is_repr=True, xml_attr=True)
    name = st.TextField(is_repr=True, xml_attr=True)
    uri = st.TextField(is_repr=True, xml_inner=True)
    quality = st.TextField(xml_attr=True)
    downloadable = st.BooleanField(xml_attr=True)
    displayable = st.BooleanField(xml_attr=True)


class Subtitle(st.BaseModel):
    attachment = st.TextField(is_repr=True)  # The relative path (example: `subtitles/sub.vtt`)
    language = st.TextField(is_repr=True)
    label = st.TextField(is_repr=True)
    visible = st.BooleanField()


class Photo(st.BaseModel):
    attachment = st.TextField(is_repr=True)  # The relative path (example: `photos/sub.vtt`)
    order = st.IntegerField(is_repr=True)
    title = st.TextField(is_repr=True)
    description = st.TextField()
    keywords = st.ListField()


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
    LAYOUT_VIDEO = 'video'
    LAYOUT_CHAPTERED = 'chaptered'
    LAYOUT_WEBINAR = 'webinar'
    LAYOUT_DUAL = 'dual'
    LAYOUTS = (LAYOUT_VIDEO, LAYOUT_CHAPTERED, LAYOUT_WEBINAR, LAYOUT_DUAL)

    title = st.TextField(is_repr=True)
    description = st.TextField()
    language = st.TextField(is_repr=True, xml_attr=True)
    item_type = st.TextField()
    layout = st.TextField(is_repr=True, xml_attr=True)
    owner = st.TextField(xml_attr=True)
    speaker = st.OneModelField(model=Speaker, xml_inner=True)
    company = st.OneModelField(model=Company, xml_inner=True)
    license = st.OneModelField(model=License, xml_inner=True)
    path = st.TextField()
    location = st.TextField()
    creation = st.DatetimeField()
    channel = st.TextField()
    categories = st.ListField()
    keywords = st.ListField()
    markers = st.ListField()
    tag_types = st.ManyModelField(model=TagType)
    indexes = st.ManyModelField(model=Index)
    resources = st.ManyModelField(model=Resource)
    subtitles = st.ManyModelField(model=Subtitle)
    photos = st.ManyModelField(model=Photo)
    data = st.JSONField()  # Additional data

    def sort_indexes(self, attr_key='time'):
        self.indexes.sort(key=lambda x: getattr(x, attr_key))
