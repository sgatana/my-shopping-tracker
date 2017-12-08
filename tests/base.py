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
            data=dict(username="stephen", email="stephen@gmail.com", password="stephen123", confirm="stephen123")
            self.client.post('v1/register', data=data)
            res = self.client.post('v1/login',
                             data=dict(
                                 email='stephen@gmail.com',
                                 password='stephen123'
                             ))
            token = json.loads(res.data)["token"]
            self.headers = {
                'Authorization': 'Brearer'+" "+token
            }



    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
            db.session.remove()

    def create_shopping_lists(self, name, description):
        """
        create a shopping list with provided details
        :param name:
        :param description:
        :return:
        """
        self.client.post(
            "/v1/Shoppinglist",
            data=dict(
                name=name,
                description=description
            ), headers=self.headers)

    def create_items(self, name, price, quantity):
        """
        create the shopping list item
        :param name:
        :param price:
        :param quantity:
        :return:
        """
        self.client.post('/v1/Shoppinglist/1/Items',
                         data=dict(
                             name=name,
                             price=price,
                             quantity=quantity
                         ), headers=self.headers)