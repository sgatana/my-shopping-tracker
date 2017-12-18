import unittest
from app import app_config
import os


class TestConfig(unittest.TestCase):
    #  set configurations in setUp
    def setUp(self):
        self.development = app_config['development']
        self.testing = app_config['testing']
        self.production = app_config['production']

    # test development configuration
    def test_development_config(self):
        self.assertTrue(self.development.DEBUG)
        self.assertTrue(self.development.SQLALCHEMY_ECHO)
        self.assertTrue(self.development.SQLALCHEMY_DATABASE_URI == os.environ.get('DB_URL'))
        self.assertFalse(self.development.SECRET_KEY is'this is my secret key')

    # test testing configurations
    def test_testing_config(self):
        self.assertFalse(self.testing.DEBUG)
        self.assertTrue(self.testing.SQLALCHEMY_DATABASE_URI == os.environ.get('TESTDB'))
        self.assertTrue(self.testing.TESTING)

    # test production configurations
    def test_production_config(self):
        self.assertFalse(self.production.DEBUG)
