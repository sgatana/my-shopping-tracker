import unittest
import json
from tests.base import BaseTest


class TestItems(BaseTest):
    """
    items testcase
    """
    def test_user_can_create_items(self):
        self.client.post('/v1/ShoppingList',
                         data=json.dumps({
                             "name": "Lunch",
                             "description": "delicious"
                         }), content_type='application/json', headers=self.headers)

        res = self.client.post('/v1/items',
                             data=json.dumps({
                                 "name": "Tea",
                                 "price": 20,
                                 "quantity": 2,
                                 "shoppinglist_id":1

                             }), content_type='application/json', headers=self.headers)

        self.assertEqual(201, res.status_code)

    def test_unregistered_user_cannot_create_shoppinglist_items(self):
        self.client.post('/v1/ShoppingList',
                         data=json.dumps({
                             "name": "Lunch",
                             "description": "delicious"
                         }), content_type='application/json', headers=self.headers)

        res = self.client.post('/v1/items',
                               data=json.dumps({
                                   "name": "Tea",
                                   "price": 20,
                                   "quantity": 2,
                                   "shoppinglist_id": 1

                               }), content_type='application/json')

        self.assertEqual(401, res.status_code)

    def test_user_can_delete_shoppinglist_items(self):
        self.create_shopping_lists("lunch", "delicious meal")
        self.create_items("Beef & rice", 200, 4, 1)
        res = self.client.delete('/v1/item/1',
                               content_type='application/json', headers=self.headers)
        print(json.loads(res.data))
        self.assertEqual(200, res.status_code)




