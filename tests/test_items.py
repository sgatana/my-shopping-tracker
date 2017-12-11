import unittest
import json
from tests.base import BaseTest


class TestItems(BaseTest):
    """
    items testcase
    """

    def test_user_can_create_items(self):
        self.create_shopping_lists('supper', 'eat a light meal')
        res = self.client.post('/v1/Shoppinglist/1/Items',
                               data=dict(
                                   name="Tea",
                                   price=20,
                                   quantity=2

                               ), headers=self.headers)
        print(json.loads(res.data))

        self.assertEqual(201, res.status_code)

    def test_user_can_get_shoppinglist_item(self):
        self.create_shopping_lists('grocery', 'dry grains at affordable price')
        self.create_items('beans', 45, 5)
        self.create_items('rice', 60, 10)
        self.create_items('maize', 80, 17)
        res = self.client.get('/v1/Shoppinglist/1/Items', headers=self.headers)
        print(json.loads(res.data))

        self.assertEqual(200, res.status_code)

    def test_unregistered_user_cannot_create_shoppinglist_items(self):
        self.create_shopping_lists('breakfast', 'delicious')
        res = self.client.post('/v1/Shoppinglist/1/Items',
                               data=dict(
                                   name="Tea",
                                   price=20,
                                   quantity=2

                               ))
        print(json.loads(res.data))

        self.assertEqual(401, res.status_code)

    def test_user_can_delete_shoppinglist_items(self):
        self.create_shopping_lists("lunch", "delicious meal")
        self.create_items('beef', 20, 2)
        res = self.client.delete('/v1/Shoppinglist/1/Items',
                                 headers=self.headers)
        print(json.loads(res.data))
        self.assertEqual(200, res.status_code)

    def test_user_can_delete_shoppinglist_item_using_id(self):
        self.create_shopping_lists("lunch", "delicious meal")
        self.create_items('beef', 20, 2)
        res = self.client.delete('/v1/Shoppinglist/1/item/1',
                                 headers=self.headers)
        print(json.loads(res.data))
        self.assertEqual(200, res.status_code)

    def test_user_can_update_item(self):
        self.create_shopping_lists("lunch", "delicious meal")
        self.create_items('beef', 20, 2)
        res = self.client.put('/v1/Shoppinglist/1/item/1',
                              data=dict(
                                  name='coffee',
                                  price=200,
                                  quantity=46
                              ),
                              headers=self.headers)
        print(json.loads(res.data))
        self.assertEqual(200, res.status_code)
