import unittest
from base64 import b64encode
from flask import json
from app import create_app, db


class BaseTest(unittest.TestCase):
    config = 'testing'
    app = create_app(config)

    def setUp(self):
        with self.app.app_context():
            db.create_all()
            db.session.commit()
            self.client = self.app.test_client()
            # self.register_user('stephen', 'stephen@gmail.com', 'stephen123')
            self.client.post('/v1/register', data=json.dumps({
                "username":"stephen",
                "email":"stephen@gmail.com",
                "password":"stephen123"
            }), content_type='application/json')

            self.headers = {
                'Authorization': 'Basic %s' % b64encode(b"stephen@gmail.com:stephen123")
                .decode("ascii")
            }

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
            db.session.remove()

