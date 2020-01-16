from magic_repr import make_repr

from api.erd.er_entities import XMLObject

__all__ = ['xmlall']


def make_init(params):
    def __init__(self, *args, **kwargs):
        self.values = []
        if len(args) == 1:
            assert all(
                [
                    any(
                        isinstance(item, class_) for class_ in params.values()
                    ) for item in args[0]
                ]
            )
            self.values = list(args[0])
        else:
            assert all(
                [
                    all(isinstance(item, params[name]) for item in values)
                    for name, values in kwargs.items()
                ]
            )
            [self.values.extend(values) for values in kwargs.values()]

    return __init__


def make_to_xml(tag_name, params):
    def to_xml(self):
        tag = self.soup.new_tag(tag_name)
        [tag.append(item.to_xml()) for item in self.values]
        return tag

    return to_xml


def make_from_xml(params):
    classes = {class_._tag_name: class_ for class_ in params.values()}

    @classmethod
    def _from_xml(cls, tag):
        return cls._make_args([
            classes[child.name].from_xml(child)
            for child in tag.find_all(True, recursive=False)
        ])

    return _from_xml


def xmlall(classname, tag_name, **params):
    class_ = type(
        classname, (XMLObject, ), {
            "__init__":
                make_init(params),
            "to_xml":
                make_to_xml(tag_name, params),
            "_from_xml":
                make_from_xml(params),
            "_tag_name":
                tag_name,
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
        }
    )
    [
        setattr(
            class_, name,
            property(
                lambda self:
                [item for item in self.values if isinstance(item, prop_class)]
            )
        ) for name, prop_class in params.items()
    ]
    class_.__repr__ = make_repr('values')
    return class_
