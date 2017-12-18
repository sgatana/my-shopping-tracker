import unittest
from flask import json
from app import create_app, db


class BaseTest(unittest.TestCase):
    """
    use base test class to define create shopping list and items methods
    """
    config = 'testing'
    app = create_app(config)

    def setUp(self):
        # set up the app_context
        with self.app.app_context():
            db.create_all()
            db.session.commit()
            self.client = self.app.test_client()
            data = dict(username="stephen", email="stephen@gmail.com", password="Stephen@123", confirm="Stephen@123")
            self.client.post('v1/register', data=data)
            res = self.client.post('v1/login',
                                   data=dict(
                                       email='stephen@gmail.com',
                                       password='Stephen@123'
                                   ))
            token = json.loads(res.data)["token"]
            self.headers = {
                'Authorization': 'Bearer' + " " + token
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

    def create_items(self, name, price, quantity, unit):
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
                             quantity=quantity,
                             unit=unit
                         ), headers=self.headers)
