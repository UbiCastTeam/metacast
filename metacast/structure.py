#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Models and fields base classes for MetaCast.
'''
import datetime
import json
from lxml import etree
try:
    strcls = unicode
except NameError:
    # Python 3
    strcls = str


# Fields
# ----------------------------------------------------------------------------
class BaseField(object):

    def __init__(self, initial=None, is_repr=False, xml_attr=False, xml_inner=False):
        object.__init__(self)
        self.name = 'filled in model init'
        self.value = initial
        self.is_repr = is_repr  # used to indicate whether this field should be used to represent the model containing it or not
        self.xml_attr = xml_attr  # only used for xml
        self.xml_inner = xml_inner

    def __repr__(self):
        return '%s=%s' % (self.name, self.value)

    def get_empty_copy(self):
        new = self.__class__(
            initial=self.get_value_copy(),
            is_repr=self.is_repr,
            xml_attr=self.xml_attr,
            xml_inner=self.xml_inner,
        )
        new.name = self.name
        return new

    def get_value_copy(self):
        return self.value

    def to_json(self):
        return self.value

    def from_json(self, data):
        self.value = data

    def to_xml(self):
        return self.value

    def from_xml(self, data):
        self.value = data


class TextField(BaseField):
    pass


class BooleanField(BaseField):

    def to_json(self):
        return True if self.value else None

    def from_json(self, data):
        self.value = True if data else None

    def to_xml(self):
        return '1' if self.value else None

    def from_xml(self, data):
        self.value = data == '1'


class IntegerField(BaseField):

    def to_xml(self):
        return str(self.value) if self.value is not None else None

    def from_xml(self, data):
        self.value = int(data) if data else None


class FloatField(BaseField):

    def to_xml(self):
        return str(self.value) if self.value is not None else None

    def from_xml(self, data):
        self.value = float(data) if data else None


class DatetimeField(BaseField):

    def get_value_copy(self):
        if not self.value:
            return None
        d = self.value
        return datetime.datetime(d.year, d.month, d.day, d.hour, d.minute, d.second)

    def to_json(self):
        if self.value:
            return self.value.strftime('%Y-%m-%d %H:%M:%S')

    def from_json(self, data):
        if data:
            self.value = datetime.datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
        else:
            self.value = None

    def to_xml(self):
        if self.value:
            return self.value.strftime('%Y-%m-%d %H:%M:%S')

    def from_xml(self, data):
        if data:
            try:
                self.value = datetime.datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                # compatibility with old versions
                self.value = datetime.datetime.strptime(data, '%Y-%m-%d_%H-%M-%S')
        else:
            self.value = None


class JSONField(BaseField):

    def to_json(self):
        return json.dumps(self.value) if self.value else None

    def from_json(self, data):
        self.value = json.loads(data) if data else None

    def to_xml(self):
        return json.dumps(self.value) if self.value else None

    def from_xml(self, data):
        self.value = json.loads(data) if data else None


class ListField(BaseField):

    def to_xml(self):
        return strcls(', ').join(self.value) if self.value else None

    def from_xml(self, data):
        self.value = [item.strip() for item in data.split(',')] if data is not None else None


class SubModelField(BaseField):

    def __init__(self, model, mono=False, *args, **kwargs):
        super(SubModelField, self).__init__(*args, **kwargs)
        self.model = model
        self.mono = mono
        self.value = list()

    def get_empty_copy(self):
        new = self.__class__(
            self.model,
            mono=self.mono,
            initial=list(),
            is_repr=self.is_repr,
            xml_attr=self.xml_attr,
            xml_inner=self.xml_inner,
        )
        new.name = self.name
        return new

    def get_value_copy(self):
        if not self.value:
            return list()
        if self.mono:
            return self.value.get_copy()
        return [m.get_copy() for m in self.value]

    def to_json(self):
        if not self.value:
            return None
        if self.mono:
            return self.value.to_json(none_if_empty=True)
        empty = True
        data = list()
        for m in self.value:
            sub = m.to_json(none_if_empty=True)
            if sub:
                empty = False
                data.append(sub)
        if empty:
            return None
        return data

    def from_json(self, data, append=False):
        if data is None or len(data) < 1:
            self.value = list()
        elif self.mono:
            self.value = self.model.from_json(data)
        else:
            if not append:
                self.value = list()
                for item in data:
                    instance = self.model.from_json(item)
                    self.value.append(instance)
            else:
                instance = self.model.from_json(data)
                self.value.append(instance)

    def to_xml(self):
        if not self.value:
            return None
        if self.mono:
            return self.value.to_xml(none_if_empty=True)
        empty = True
        nodes = list()
        for m in self.value:
            sub = m.to_xml(none_if_empty=True)
            if sub is not None:
                empty = False
                nodes.append(sub)
        if empty:
            return None
        return nodes

    def from_xml(self, data, append=False):
        if data is None or len(data) < 1:
            self.value = list()
        elif self.mono:
            self.value = self.model.from_xml(data[0])
        else:
            if not append:
                self.value = list()
            for item in data:
                instance = self.model.from_xml(item)
                self.value.append(instance)


class OneModelField(SubModelField):

    def __init__(self, *args, **kwargs):
        kwargs['mono'] = True
        super(OneModelField, self).__init__(*args, **kwargs)


class ManyModelField(SubModelField):

    def __init__(self, *args, **kwargs):
        kwargs['mono'] = False
        super(ManyModelField, self).__init__(*args, **kwargs)


# Models
# ----------------------------------------------------------------------------
class BaseModel(object):
    ORDER = {None: 0, True: 1, False: 2}  # used to set order of appearance in exports

    def __init__(self, *args, **kwargs):
        object.__init__(self)
        if hasattr(self, 'fields'):
            raise AttributeError('You have used a reserved name of model: "fields".')
        self.__class__._init()
        self.fields = list()
        self.fields_dict = dict()
        for field in self.__class__._fields:
            copy = field.get_empty_copy()
            if field.name in kwargs:
                copy.value = kwargs[field.name]
            self.fields.append(copy)
            self.fields_dict[field.name] = copy
        if not self.fields:
            raise AttributeError('No fields found for model %s.' % self.__class__.__name__)

    def __repr__(self):
        props = list()
        for field in self.fields:
            if field.is_repr:
                props.append(str(field))
        return '%s(%s)' % (self.__class__.__name__, ','.join(props))

    @classmethod
    def _init(cls):
        if hasattr(cls, '_initialized'):
            return
        cls_fields = list()
        cls_fields_dict = dict()
        for name in dir(cls):
            field = getattr(cls, name)
            if isinstance(field, BaseField):
                field.name = name
                cls_fields.append(field)
                cls_fields_dict[name] = field
                cls._init_proerty(name)
        cls_fields.sort(key=lambda f: (cls.ORDER[getattr(f, 'mono', None)], f.name))
        cls._fields = cls_fields
        cls._fields_dict = cls_fields_dict
        cls._initialized = True

    @classmethod
    def _init_proerty(cls, name):
        setattr(cls, name, property(
            lambda instance: instance._get_field(name),  # get
            lambda instance, value: instance._set_field(name, value),  # set
            lambda instance: None,  # del
            name
        ))

    def _get_field(self, name):
        return self.fields_dict[name].value

    def _set_field(self, name, value):
        self.fields_dict[name].value = value

    def get_copy(self):
        kwargs = dict()
        for field in self.fields:
            kwargs[field.name] = field.get_copy()
        return self.__class__(**kwargs)

    def to_json(self, none_if_empty=False):
        empty = True
        data = dict()
        for field in self.fields:
            val = field.to_json()
            if val is None:
                continue
            empty = False
            data[field.name] = val
        if empty and none_if_empty:
            return None
        return data

    @classmethod
    def from_json(cls, data):
        new = cls()
        if data:
            if not isinstance(data, dict):
                raise Exception('Invalid data given to function from_json.')
            for field in new.fields:
                if field.name in data:
                    field.from_json(data[field.name])
        return new

    def to_xml(self, none_if_empty=False):
        empty = True
        parent = etree.Element(self.__class__.__name__.lower())
        for field in self.fields:
            val = field.to_xml()
            if val is None:
                continue
            empty = False
            if field.xml_attr:
                parent.set(field.name, val)
            else:
                node = parent if field.xml_inner else etree.Element(field.name)
                if isinstance(field, SubModelField):
                    if field.mono:
                        node.append(val)
                    else:
                        for el in val:
                            node.append(el)
                else:
                    node.text = val
                if not field.xml_inner:
                    parent.append(node)
        if empty and none_if_empty:
            return None
        return parent

    @classmethod
    def from_xml(cls, node):
        new = cls()
        for field in new.fields:
            if isinstance(field, SubModelField):
                children = None
                if field.xml_inner:
                    children = node.findall(field.model.__name__.lower())
                else:
                    parent = node.find(field.name)
                    if parent is not None:
                        children = parent.findall(field.model.__name__.lower())
                field.from_xml(children)
            elif field.xml_attr:
                field.from_xml(node.get(field.name))
            elif field.xml_inner:
                field.from_xml(node.text)
            else:
                child = node.find(field.name)
                if child is not None:
                    field.from_xml(child.text)
        return new
