import unittest
from flask import json
from app import create_app, db


class TestEndpoints(unittest.TestCase):
    # set the app context in the setUp
    def setUp(self):
        config = 'testing'
        self.app = create_app(config)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

        # set register method to log in user
    def register_user(self):
        self.client.post('/v1/register', data=dict(username="steve", email="steve@gmail.com", password="Steve@123",
                                                   confirm="Steve@123"))

    # test user registration
    def test_user_can_register(self):
        response = self.client.post('/v1/register',
                                    data=dict(username="steve", email="steve@gmail.com", password="Steve@123",
                                              confirm="Steve@123"))
        self.assertEqual(201, response.status_code)

    # test user login
    def test_only_registered_user_can_login(self):
        self.register_user()
        response = self.client.post('/v1/login',
                                    data=dict(
                                        email="steve@gmail.com",
                                        password="Steve@123"
                                    ))
        self.assertEqual(200, response.status_code)

    # test unauthorized users
    def test_registered_users_cannot_login_with_wrong_credentials(self):
        self.register_user()
        response = self.client.post('/v1/login',
                                    data=dict(
                                        email="steve@gmail.com",
                                        password="steve1234"
                                    ))
        self.assertEqual(401, response.status_code)

    # test unauthorized user cannot login
    def test_non_registered_user_cannot_login(self):
        response = self.client.post('/v1/login',
                                    data=dict(
                                        email="steve@gmail.com",
                                        password="Steve123"
                                    ))
        self.assertEqual(401, response.status_code)

    # test user can logout
    def test_user_can_logout(self):
        self.register_user()
        res = self.client.post('v1/login',
                               data=dict(
                                   email='steve@gmail.com',
                                   password='Steve@123'
                               ))

        token = json.loads(res.data)["token"]
        self.headers = {
            'Authorization': 'Bearer' + " " + token
        }
        response = self.client.post('/v1/logout',
                                    headers=self.headers)
        print(response.data)
        self.assertEqual(response.status_code, 200)

    # test page not found error handler
    def test_page_not_found(self):
        response = self.client.get('/andela')
        self.assertEqual(response.status_code, 404)

    # test user profile
    def test_user_can_load_profile_details(self):
        self.register_user()
        res = self.client.post('v1/login',
                               data=dict(
                                   email='steve@gmail.com',
                                   password='Steve@123'
                               ))
        token = json.loads(res.data)["token"]
        self.headers = {
            'Authorization': 'Bearer' + " " + token
        }
        response = self.client.get('/v1/user',
                                   headers=self.headers)

        self.assertEqual(response.status_code, 200)