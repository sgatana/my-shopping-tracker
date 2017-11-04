import unittest
from app import app_config
import os


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.development = app_config['development']
        self.testing = app_config['testing']
        self.production = app_config['production']

    def test_development_config(self):
        self.assertTrue(self.development.DEBUG)
        self.assertEqual(self.development.SQLALCHEMY_DATABASE_URI, os.environ.get('DevelopmentBD'))
        self.assertTrue(self.development.SQLALCHEMY_ECHO)
        self.assertFalse(self.development.SECRET_KEY is'hello')

    def test_testing_config(self):
        self.assertTrue(self.testing.DEBUG)
        self.assertTrue(self.testing.SQLALCHEMY_DATABASE_URI == os.environ.get('TestDB'))
        self.assertTrue(self.testing.TESTING)

    def test_production_config(self):
        self.assertFalse(self.production.DEBUG)
