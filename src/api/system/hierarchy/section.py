from .elements import (_element_attrs, _element_children_classes, _element_kws,
                       _element_types)
from .xmllist import xmllist
from .xmltag import xmltag
from .xmltuple import xmltuple

__all__ = ['Section', 'Children']

ChildId = xmltag('ChildId', 'childId', int)
Children = xmllist('Children', 'children', ChildId)
_Section = xmltuple(
    '_Section', 'section', [*_element_attrs, 'children'],
    [*_element_children_classes, Children], _element_kws, _element_types
)


class Section(_Section):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.children is None:
            self.children = Children()
        self._children = None

    def resolve_children(self, func):
        self._children = [func(id) for id in self.children]
        return self.children.values

    def resolve_rights(self):
        for child in self._children:
            if child.accessRights.inherit:
                child.accessRights.copy_rights(self.accessRights)
            if isinstance(child, Section):
                child.resolve_rights()

    def to_object(self, add_name=False):
        obj = super().to_object(add_name)
        if self._children:
            obj['children'] = [child.to_object() for child in self._children]
        return obj
