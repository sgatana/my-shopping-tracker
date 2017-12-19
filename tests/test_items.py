import unittest
import json
from tests.base import BaseTest


class TestItems(BaseTest):
    """
    items testcase
    """

    # test user can create items to a specific shopping list
    def test_user_can_create_items(self):
        self.create_shopping_lists('supper', 'eat a light meal')
        res = self.client.post('/v1/Shoppinglist/1/Items',
                               data=dict(
                                   name="Tea",
                                   price=20,
                                   quantity=2,
                                   unit="kgs"

                               ), headers=self.headers)

        self.assertEqual(201, res.status_code)

    # test unauthorized user cannot create items to a specific shopping list
    def test_non_user_cannot_create_items(self):
        self.create_shopping_lists('supper', 'eat a light meal')
        res = self.client.post('/v1/Shoppinglist/1/Items',
                               data=dict(
                                   name="Tea",
                                   price=20,
                                   quantity=2,
                                   unit="kgs"

                               ))

        self.assertEqual(401, res.status_code)

    # test user can query all the items from a shopping list
    def test_user_can_get_shoppinglist_item(self):
        self.create_shopping_lists('grocery', 'dry grains at affordable price')
        self.create_items('beans', 45, 5, "kgs")
        self.create_items('rice', 60, 10, "kgs")
        self.create_items('maize', 80, 17, "kgs")
        res = self.client.get('/v1/Shoppinglist/1/Items', headers=self.headers)
        self.assertEqual(3, len(json.loads(res.data).get("shoppinglist_items")))
        self.assertEqual(200, res.status_code)

    # test unauthorized user is forbidden from accessing items
    def test_unregistered_user_cannot_create_shoppinglist_items(self):
        self.create_shopping_lists('breakfast', 'delicious')
        res = self.client.post('/v1/Shoppinglist/1/Items',
                               data=dict(
                                   name="Tea",
                                   price=20,
                                   quantity=2,
                                   unit="kgs"

                               ))

        self.assertEqual(401, res.status_code)

    # test user can delete shopping list
    def test_user_can_delete_shoppinglist_items(self):
        self.create_shopping_lists("lunch", "delicious meal")
        self.create_items('beef', 20, 2, "kgs")
        res = self.client.delete('/v1/Shoppinglist/1/Items',
                                 headers=self.headers)
        self.assertEqual(200, res.status_code)

    # test user can delete a single item
    def test_user_can_delete_shoppinglist_item_using_id(self):
        self.create_shopping_lists("lunch", "delicious meal")
        self.create_items('beef', 20, 2, "g")
        res = self.client.delete('/v1/Shoppinglist/1/Items/1',
                                 headers=self.headers)
        self.assertEqual(200, res.status_code)

    # test use can update an item
    def test_user_can_update_item(self):
        self.create_shopping_lists("lunch", "delicious meal")
        self.create_items('beef', 20, 2, "g")
        res = self.client.put('/v1/Shoppinglist/1/Items/1',
                              data=dict(
                                  name='coffee',
                                  price=200,
                                  quantity=46,
                                  unit="kgs"
                              ),
                              headers=self.headers)
        self.assertEqual(200, res.status_code)
