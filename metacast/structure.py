'''
Models and fields base classes for MetaCast.
'''
import datetime
import json
import logging
from lxml import etree
logger = logging.getLogger(__name__)


class BaseField:

    def __init__(self, initial=None, is_repr=False, xml_attr=False, xml_inner=False):
        self.name = 'filled in model init'
        self.value = initial
        self.initial = initial
        # "is_repr" is used to indicate whether this field should be used to represent the model
        self.is_repr = is_repr
        # "xml_attr" is used to indicate if the field value should be put as attribute in XML files
        self.xml_attr = xml_attr
        # "xml_inner" is used to indicate if the field value should be put as tag content in XML files
        self.xml_inner = xml_inner

    def __repr__(self):
        return f'{self.name}={self.value}'

    def set_initial(self):
        if callable(self.initial):
            self.value = self.initial()
        else:
            self.value = self.initial

    def get_empty_copy(self):
        new = self.__class__(
            initial=self.initial,
            is_repr=self.is_repr,
            xml_attr=self.xml_attr,
            xml_inner=self.xml_inner,
        )
        new.name = self.name
        new.set_initial()
        return new

    def get_value_copy(self):
        return self.value

    def to_any(self):
        if self.value != self.initial:
            return self.value

    def from_any(self, data):
        if data is None:
            self.set_initial()
        else:
            self.value = data

    def to_json(self):
        return self.to_any()

    def from_json(self, data):
        return self.from_any(data)

    def to_xml(self):
        return self.to_any()

    def from_xml(self, data):
        return self.from_any(data)


class TextField(BaseField):

    def __init__(self, *args, **kwargs):
        if kwargs.get('initial') is None:
            kwargs['initial'] = ''
        super().__init__(*args, **kwargs)

    def to_any(self):
        value = super().to_any()
        if value is not None and not isinstance(value, str):
            value = str(value)
        return value


class BooleanField(BaseField):

    def __init__(self, *args, **kwargs):
        if kwargs.get('initial') is None:
            kwargs['initial'] = False
        super().__init__(*args, **kwargs)

    def to_json(self):
        if self.value != self.initial:
            return True if self.value else False

    def from_json(self, data):
        if data is None:
            self.set_initial()
        else:
            self.value = True if data else False

    def to_xml(self):
        if self.value != self.initial:
            return '1' if self.value else '0'

    def from_xml(self, data):
        if data is None:
            self.set_initial()
        else:
            self.value = data == '1'


class IntegerField(BaseField):

    def __init__(self, *args, **kwargs):
        if kwargs.get('initial') is None:
            kwargs['initial'] = 0
        super().__init__(*args, **kwargs)

    def to_xml(self):
        if self.value is not None and self.value != self.initial:
            return str(self.value)

    def from_xml(self, data):
        if data is None:
            self.set_initial()
        else:
            self.value = int(data)


class FloatField(BaseField):

    def __init__(self, *args, **kwargs):
        if kwargs.get('initial') is None:
            kwargs['initial'] = 0.0
        super().__init__(*args, **kwargs)

    def to_xml(self):
        if self.value is not None and self.value != self.initial:
            return str(self.value)

    def from_xml(self, data):
        if data is None:
            self.set_initial()
        else:
            self.value = float(data)


class DatetimeField(BaseField):

    def get_value_copy(self):
        if not self.value:
            return None
        d = self.value
        return datetime.datetime(d.year, d.month, d.day, d.hour, d.minute, d.second)

    def to_any(self):
        if self.value != self.initial and self.value:
            return self.value.strftime('%Y-%m-%d %H:%M:%S')

    def from_any(self, data):
        if data is None:
            self.set_initial()
        elif data:
            try:
                self.value = datetime.datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                # compatibility with old versions
                self.value = datetime.datetime.strptime(data, '%Y-%m-%d_%H-%M-%S')
        else:
            self.value = None


class JSONField(BaseField):

    def __init__(self, *args, **kwargs):
        if kwargs.get('initial') is None:
            kwargs['initial'] = dict
        super().__init__(*args, **kwargs)

    def to_json(self):
        if self.value != self.initial and self.value:
            if not isinstance(self.value, dict):
                raise ValueError('Invalid value for JSONField.')
            return self.value

    def to_xml(self):
        if self.value != self.initial and self.value:
            if not isinstance(self.value, dict):
                raise ValueError('Invalid value for JSONField.')
            return json.dumps(self.value, sort_keys=True)

    def from_any(self, data):
        if data is None:
            self.set_initial()
        elif isinstance(data, str):
            self.value = json.loads(data)
        elif isinstance(data, dict):
            self.value = data
        else:
            raise ValueError('Invalid data for JSONField.')


class ListField(BaseField):

    def __init__(self, *args, **kwargs):
        if kwargs.get('initial') is None:
            kwargs['initial'] = list
        super().__init__(*args, **kwargs)

    def to_json(self):
        if self.value != self.initial and self.value:
            return self.value

    def to_xml(self):
        if self.value != self.initial and self.value:
            return ', '.join(self.value)

    def from_xml(self, data):
        if data is None:
            self.set_initial()
        else:
            self.value = [item.strip() for item in data.split(',')]


class SubModelField(BaseField):

    def __init__(self, model, mono=False, *args, **kwargs):
        # Changing initial value for this field is not allowed
        kwargs['initial'] = list
        super().__init__(*args, **kwargs)
        self.model = model
        self.mono = mono

    def get_empty_copy(self):
        new = self.__class__(
            self.model,
            mono=self.mono,
            initial=self.initial,
            is_repr=self.is_repr,
            xml_attr=self.xml_attr,
            xml_inner=self.xml_inner,
        )
        new.name = self.name
        new.set_initial()
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
            self.set_initial()
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
            self.set_initial()
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
        super().__init__(*args, **kwargs)
        self.initial = None


class ManyModelField(SubModelField):

    def __init__(self, *args, **kwargs):
        kwargs['mono'] = False
        super().__init__(*args, **kwargs)


class BaseModel:
    ORDER = {None: 0, True: 1, False: 2}  # Used to set order of appearance in exports

    def __init__(self, *args, **kwargs):
        if args:
            raise ValueError('Non-keyword arguments are not accepted')
        if hasattr(self, 'fields'):
            raise AttributeError('You have used a reserved name of model: "fields".')
        self.__class__._init()
        self.fields = list()
        self.fields_dict = dict()
        for field in self.__class__._fields:
            copy = field.get_empty_copy()
            if field.name in kwargs:
                copy.value = kwargs.pop(field.name)
            self.fields.append(copy)
            self.fields_dict[field.name] = copy
        if not self.fields:
            raise AttributeError('No fields found for model %s.' % self.__class__.__name__)
        if kwargs:
            raise ValueError('Invalid keyword arguments: %s' % ', '.join(kwargs.keys()))

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
                raise ValueError('Invalid data given to function "from_json".')
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
                try:
                    parent.set(field.name, val)
                except Exception as err:
                    logger.error(
                        f'Error when trying to serialize attribute "{field.name}" '
                        f'of model "{self.__class__.__name__}" to XML: {err}'
                    )
                    # Try to log the expected content of the node, without crashing if it fails
                    try:
                        logger.error(f'Field value: "{val}", type: "{type(val)}"')
                    except Exception:
                        pass
                    raise
            else:
                node = parent if field.xml_inner else etree.Element(field.name)
                if isinstance(field, SubModelField):
                    if field.mono:
                        node.append(val)
                    else:
                        for el in val:
                            node.append(el)
                else:
                    try:
                        node.text = val
                    except Exception as err:
                        logger.error(
                            f'Error when trying to serialize field "{field.name}" '
                            f'of model "{self.__class__.__name__}" to XML: {err}'
                        )
                        # Try to log the expected content of the node, without crashing if it fails
                        try:
                            logger.error(f'Field value: "{val}", type: "{type(val)}"')
                        except Exception:
                            pass
                        raise
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
