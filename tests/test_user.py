import unittest
from app import create_app, db
from app.Api_models.users import User


class UserTest(unittest.TestCase):
    app = create_app('testing')
    app.app_context().push()
    db.drop_all()
    db.create_all()

    def setUp(self):
        self.user = User(username='steve', email='steve@gmail.com', password='steve@2017')
        self.token = self.user.encode_auth_token('id')

    def test_set_password_hash(self):
        self.assertNotEqual(self.user.password, "steve@2017")

    def test_verify_password(self):
        self.assertTrue(self.user.password,
                        self.user.verify_password("steve@2017"))

    def test_generate_token(self):
        self.assertTrue(self.user.encode_auth_token('id'))



