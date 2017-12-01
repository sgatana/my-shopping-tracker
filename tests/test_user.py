import unittest
from app import create_app, db
from app.Api_models.users import User


class UserTest(unittest.TestCase):
    app = create_app('testing')
    app.app_context().push()
    db.drop_all()
    db.create_all()

    def setUp(self):
        self.user = User(username='steve', email='steve@gmail.com', password='steve@2017', confirm='steve@2017')
        self.token = self.user.generate_auth_token(expiration=50, config='testing')

    def test_set_password_hash(self):
        self.assertNotEqual(self.user.password, "steve@2017")

    def test_verify_password(self):
        self.assertTrue(self.user.password,
                        self.user.verify_password("steve@2017"))

    def test_generate_token(self):
        self.assertTrue(self.user.generate_auth_token(expiration=50, config='testing'))

    def test_token_expire_after_given_time(self):
        self.assertNotEqual(self.user.generate_auth_token(expiration=50, config='testing'),
        self.user.generate_auth_token(expiration=100, config='testing'))

