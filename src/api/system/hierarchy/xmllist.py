from collections.abc import Iterable

from magic_repr import make_repr

from api.erd.er_entities import XMLObject

__all__ = ['xmllist']


def make_init(kws):
    def __init__(self, values=None, *args, **kwargs):
        self.values = []
        if values is None:
            return
        if not isinstance(values, Iterable):
            values = [values]
        [setattr(self, key, None) for key in kws]
        [setattr(self, key, value) for key, value in zip(kws, args)]
        [setattr(self, key, value) for key, value in kwargs.items()]
        self.values = values

    return __init__


def make_to_xml(tag_name, children_class, children_tag):
    def to_xml(self):
        tag = self.soup.new_tag(tag_name)
        if children_class is not None:
            [tag.append(value.to_xml()) for value in self.values]
        else:
            [
                tag.append(self.new_tag(children_tag, value))
                for value in self.values
            ]
        [
            tag.__setitem__(key, value)
            for key, value in self.__dict__.items() if key != 'values'
        ]
        return tag

    return to_xml


def make_from_xml(children_class):
    @classmethod
    def from_xml(cls, tag):
        if children_class is not None:
            values = [
                children_class.from_xml(child)
                for child in tag.find_all(True, recursive=False)
            ]
        else:
            values = [
                child.text for child in tag.find_all(True, recursive=False)
            ]
        return cls._make_args(values=values, **tag.attrs)

    return from_xml


def xmllist(classname, tag_name, children, kws=[]):
    children_class, children_tag = None, None
    if isinstance(children, type):
        children_class = children
    else:
        children_tag = children
    class_ = type(
        classname, (XMLObject, ), {
            "__init__":
                make_init(kws),
            "to_xml":
                make_to_xml(tag_name, children_class, children_tag),
            "_from_xml":
                make_from_xml(children_class),
            "__len__":
                lambda self: len(self.values),
            "__getitem__":
                lambda self, key: self.values.__getitem__(key),
            "__setitem__":
                lambda self, key, value: self.values.__setitem__(key, value),
            "__delitem__":
                lambda self, key: self.values.__delitem__(key),
            "__iter__":
                lambda self: self.value.__iter_,
            "append":
                lambda self, item: self.values.append(item),
            "_tag_name":
                tag_name
        }
    )
    class_.__repr__ = make_repr('values', *kws)
    return class_
