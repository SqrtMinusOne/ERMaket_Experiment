import importlib
import logging
import os
from fnmatch import fnmatch

from marshmallow_sqlalchemy import ModelConversionError, SQLAlchemyAutoSchema

from ermaket.api import Config
from ermaket.api.database import DBConn
from ermaket.utils import Singleton, get_project_root

# from sqlalchemy.inspection import inspect
# from marshmallow_sqlalchemy.fields import Nested

__all__ = ['Models']


class Models(metaclass=Singleton):
    """A class for managing the SQLAlchemy models directory.
    As models are generated classes, they have to be imported dynamically.

    Models are separated by schemas; schemas can be accessed as this class'
    attributes.

    related config.json parameters: Models
    """

    def __init__(self, system_only=False):
        if DBConn.engine is None:
            DBConn()
        self.config = Config()
        self.schemas = {}
        self.Base = None
        self._paths = {}
        self._import_base()
        self._system_only = system_only
        self._import()

    def _import_base(self):
        filename = f"{self.config.Models['models_dir']}.base".replace('/', '.')
        filename = f"{self.config.Models['package']}.{filename}"
        module = importlib.import_module(filename)
        self.Base = getattr(module, 'Base')

    @property
    def _root(self):
        return os.path.join(
            get_project_root(), self.config.Models['models_dir']
        )

    def _import(self):
        loaded = 0
        found = []
        for subdir, _, files in os.walk(self._root):
            for f in files:
                if (
                    fnmatch(f, f"{self.config.Models['model_prefix']}*.py") and
                    not self._system_only
                ):
                    found.append(os.path.join(subdir, f))
                elif fnmatch(f, f"{self.config.Models['system_prefix']}*.py"):
                    found.append(os.path.join(subdir, f))
        found = [
            os.path.relpath(p, get_project_root()) for p in found
        ]
        loaded = self._import_files(found)
        self._setup_marshmallows()
        if not self._system_only:
            logging.info(f'Schemas loaded: {len(self.schemas)}')
            logging.info(f'Models loaded: {loaded}')
        else:
            logging.info(f'Loaded system models: {loaded}')

    def _import_files(self, files):
        loaded = 0
        for filename in files:
            module_name = filename.replace('/', '.')[:-3]
            module_name = f"{self.config.Models['package']}.{module_name}"
            module = importlib.import_module(module_name)

            for class_name in module.__all__:
                model = getattr(module, class_name)
                schema = model.__table__.schema
                try:
                    self.schemas[schema][class_name] = model
                    self._paths[schema][class_name] = module_name
                except KeyError:
                    self.schemas[schema] = {class_name: model}
                    self._paths[schema] = {class_name: module_name}
                loaded += 1
                setattr(model, '__module_name__', module_name)
        return loaded

    def _setup_marshmallows(self):
        for model in self.__iter__():
            self._setup_marshmallow(model)

    def _marsh_name(self, class_):
        schema_class_name = f"{class_.__name__}Schema"
        return schema_class_name

    def _setup_marshmallow(self, class_):
        if class_.__name__.endswith("Schema"):
            raise ModelConversionError(
                "For safety, setup_schema can not be used when a"
                "Model class ends with 'Schema'"
            )

        class Meta(object):
            model = class_
            # sqla_session = DBConn.scoped_session
            include_fk = True
            load_instance = True
            include_relationships = True

        # for rel in inspect(class_).relationships:
        #     to_nest = rel.mapper.class_
        #     only = [col.name for col in to_nest.__table__.columns]
        #     nested = Nested(self._marsh_name(to_nest), many=True, only=only)
        #     setattr(Meta, rel.class_attribute.key, nested)

        schema_class_name = self._marsh_name(class_)
        schema_class = type(
            schema_class_name, (SQLAlchemyAutoSchema, ), {"Meta": Meta}
        )
        setattr(class_, "__marshmallow__", schema_class)

    @property
    def schema_names(self):
        return list(self.schemas.keys())

    def __getattr__(self, key):
        return self.schemas[key]

    def __getitem__(self, key):
        return self.__getattr__(key)

    def __iter__(self):
        for schema in self.schemas.values():
            for table in schema.values():
                yield table
