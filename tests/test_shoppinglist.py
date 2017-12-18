import json
from tests.base import BaseTest


class ShoppinglistTestcase(BaseTest):
    """
    this class represents shoppinglist testcase
    """

    def test_shoppinglist_creation(self):
        response = self.client.post('/v1/Shoppinglist',
                                    data=dict(
                                        name="supper",
                                        description="very delicious"
                                    ), headers=self.headers)
        self.assertEqual(201, response.status_code)

    def test_get_shoppinglist(self):
        self.create_shopping_lists('supper', 'delicious')
        response = self.client.get('/v1/Shoppinglist', headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_delete_all_shopping_lists(self):
        self.create_shopping_lists('supper', 'delicious meal')
        response = self.client.delete('/v1/Shoppinglist', headers=self.headers)

        self.assertEqual(response.status_code, 200)

    def test_unauthorized_users_cannot_create_shoppinglist(self):
        res = self.client.post('/v1/Shoppinglist',
                               data=dict(
                                   name="supper",
                                   description="very delicious"
                               ))
        self.assertEqual(401, res.status_code)

    def test_Update_shoppinglist(self):
        self.create_shopping_lists("Lunch", "The best meal for the day")
        response = self.client.put('/v1/Shoppinglist/1',
                                   data=dict(
                                       name="supper",
                                       description="very delicious"
                                   ), headers=self.headers)
        self.assertEqual(200, response.status_code)

    def test_user_can_get_shopping_list_with_given_id(self):
        self.create_shopping_lists("Lunch", "The best meal for the day")
        response = self.client.get('/v1/Shoppinglist/1', headers=self.headers)
        self.assertEqual(200, response.status_code)

    def test_non_existing_shoppinglist_cannot_be_updated(self):
        response = self.client.put('/v1/Shoppinglist/12',
                                   data=dict(
                                       name="supper",
                                       description="very delicious"
                                   ), headers=self.headers)
        self.assertEqual(response.status_code, 404)

    def test_delete_shoppinglist(self):
        self.create_shopping_lists("Lunch", "a delicious meal")
        res = self.client.delete('/v1/Shoppinglist/1', headers=self.headers)
        self.assertEqual(200, res.status_code)
