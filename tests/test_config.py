import unittest
from app import app_config


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.development = app_config['development']
        self.testing = app_config['testing']
        self.production = app_config['production']

    def test_development_config(self):
        self.assertTrue(self.development.DEBUG)
        self.assertEqual(self.development.SQLALCHEMY_DATABASE_URI,  "postgresql://postgres:steve012@localhost/flask_api")
        self.assertTrue(self.development.SQLALCHEMY_ECHO)
        self.assertEqual(self.development.SECRET_KEY, 'hellofromtheotherside')

    def test_testing_config(self):
        self.assertTrue(self.testing.DEBUG)
        self.assertEqual(self.testing.SQLALCHEMY_DATABASE_URI,  "postgresql://postgres:steve012@localhost/test_db")
        self.assertTrue(self.testing.TESTING)

    def test_production_config(self):
        self.assertFalse(self.production.DEBUG)
        self.assertFalse(self.production.TESTING)