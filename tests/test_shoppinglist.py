import json
from tests.base import BaseTest


class ShoppinglistTestcase(BaseTest):
    """
    this class represents shoppinglist testcase
    """
    def test_shoppinglist_creation(self):
        response = self.client.post('/v1/ShoppingList',
                               data=json.dumps({
                                   "name": "supper",
                                   "description": "eat light meal"
                               }),
                               content_type='application/json',
                               headers=self.headers)
        self.assertEqual(200, response.status_code)

    def test_get_shoppinglist(self):
        response=self.client.get('/v1/ShoppingList', headers=self.headers)
        print(json.loads(response.data))
        self.assertTrue(len(json.loads(response.data)))
        print(json.loads(response.data))

    def test_unauthorized_users_cannot_create_shoppinglist(self):
        res = self.client.post('/v1/ShoppingList',
                               data=json.dumps({
                                   "name": "babab",
                                   "description": "jsakdkj"
                               }),
                               content_type='application/json'
                               )
        self.assertEqual(401, res.status_code)

    def test_Update_shoppinglist(self):
        self.create_shopping_lists("Lunch", "The best meal for the day")
        response=self.client.put('/v1/ShoppingList/1',
                                 data=json.dumps({
                                     "name":"updated name",
                                     "description":"updated shoppinglist"
                                 }), content_type='application/json', headers=self.headers)
        self.assertEqual(200, response.status_code)

    def test_non_existing_shoppinglist_cannot_be_updated(self):
        response = self.client.put('/v1/ShoppingList/12',
                                   data=json.dumps({
                                       "name": "updated name",
                                       "description": "updated shoppinglist"
                                   }), content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 404)



