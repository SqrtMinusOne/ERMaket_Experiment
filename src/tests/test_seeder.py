import unittest

from api.config import Config
from api.database import DBConn
from api.models import Faker, Models, Seeder


class TestSeeder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Config(reload=True)
        DBConn()

    def test_seeder(self):
        models = Models()
        seeder = Seeder(models)
        seeder.drop_models()
        seeder.drop_models()
        seeder.create_models()
        seeder.drop_models()
        seeder.drop_models()

    def test_faker(self):
        models = Models()
        seeder = Seeder(models)
        faker = Faker(models)
        seeder.drop_models()
        seeder.create_models()
        faker.fake_all(10)
        with DBConn.get_session() as db:
            for table in iter(models):
                self.assertTrue(db.query(table).first())
