from utils import caster, defaultify_init

from .elements import (_element_attrs, _element_children_classes, _element_kws,
                       _element_types)
from .form import FormDescription, LinkedField, LinkType, SimpleField
from .xmlall import xmlall
from .xmlenum import xmlenum
from .xmltuple import xmltuple

__all__ = [
    'Table', 'TableColumn', 'TableColumns', 'TableLinkType',
    'LinkedTableColumn'
]

_table_column_attrs = [
    'rowName', 'text', 'isSort', 'isFilter', 'isEditable', 'isPk',
    'isRequired', 'type', 'dateFormat'
]

_table_column_types = {
    'isPk': caster.bool_cast,
    'isSort': caster.bool_cast,
    'isFilter': caster.bool_cast,
    'isEditable': caster.bool_cast,
    'isRequired': caster.bool_cast,
}

_TableColumn = xmltuple(
    '_TableColumn',
    'column',
    _table_column_attrs,
    types=_table_column_types,
)

TableColumn = defaultify_init(
    _TableColumn,
    'TableColumn',
    text=lambda s: s.rowName,
    isPk=False,
    isSort=True,
    isFilter=True,
    isEditable=True
)

TableLinkType = xmlenum(
    'TableLinkType',
    'linkType',
    SIMPLE='simple',
    DROPDOWN='dropdown',
    LINKED='linked'
)

_link_type_mappings = {}
_link_type_mappings[TableLinkType.SIMPLE] = LinkType.SIMPLE
_link_type_mappings[TableLinkType.DROPDOWN] = LinkType.DROPDOWN
_link_type_mappings[TableLinkType.LINKED] = LinkType.LINKEDFORM

_LinkedTableColumn = xmltuple(
    '_LinkedTableColumn',
    'linkedColumn', [
        *_table_column_attrs,
        'linkTableName',
        'linkSchema',
        'linkType',
        'fkName',
        'isMultiple',
    ], [TableLinkType],
    types={
        **_table_column_types,
        'isMultiple': caster.bool_cast,
    }
)

LinkedTableColumn = defaultify_init(
    _LinkedTableColumn,
    'LinkedTableColumn',
    text=lambda s: s.rowName,
    isPk=False,
    isSort=True,
    isFilter=True,
    isEditable=True,
    linkType=lambda s: TableLinkType(TableLinkType.SIMPLE)
    if s.fkName else TableLinkType(TableLinkType.LINKED)
)

TableColumns = xmlall(
    'TableColumns', 'columns', normal=TableColumn, linked=LinkedTableColumn
)

__Table = xmltuple(
    '__Table', 'tableEntry', [
        *_element_attrs, 'tableName', 'schema', 'linesOnPage', 'columns',
        'formDescription', 'pagination'
    ], [*_element_children_classes, TableColumns, FormDescription],
    _element_kws, {
        **_element_types, 'linesOnPage': int,
        'pagination': caster.bool_cast
    }
)

_Table = defaultify_init(
    __Table,
    '_Table',
    linesOnPage=50,
    columns=lambda self: TableColumns(),
    tableName=lambda self: self.name,
    pagination=True
)


class Table(_Table):
    def make_form(self):
        form = FormDescription(self.schema, self.tableName)
        for column in self.columns:
            if column._tag_name == 'column':
                form.fields.append(
                    SimpleField(
                        tableField=column.rowName,
                        text=column.text,
                        isEditable=True
                    )
                )
            else:
                form.fields.append(
                    LinkedField(
                        tableField=column.rowName,
                        text=column.text,
                        isEditable=True,
                        linkType=_link_type_mappings[column.linkType.value],
                        linkSchema=column.linkSchema,
                        linkTableName=column.linkTableName
                    )
                )
        return form
