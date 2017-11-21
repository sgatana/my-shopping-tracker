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

    def create_shopping_lists(self, name, description):
        """
        create a shopping list with provided details
        :param name:
        :param description:
        :return:
        """
        self.client.post(
            "/v1/ShoppingList",
            data=json.dumps({
                "name":name,
                "description": description
            }),
            content_type='application/json', headers=self.headers)

    def create_items(self, name, price, quantity, shoppinglist_id):
        """
        create the shopping list item
        :param name:
        :param price:
        :param quantity:
        :param shoppinglist_id:
        :return:
        """
        self.client.post('/v1/items',
                         data=json.dumps({
                             "name": name,
                             "price": price,
                             "quantity": quantity,
                             "shoppinglist_id": shoppinglist_id
                         }), content_type='application/json', headers=self.headers)