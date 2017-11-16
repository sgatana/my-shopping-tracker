from flask_restplus import fields, Namespace
from . import item, users, shoppinglist

ns = Namespace('API', description='ShoppingList Endpoints')

# Model Schemas

register_model = ns.model('register', {
    'username': fields.String(required=True, default="username"),
    'email': fields.String(required=True, default="user@example.com"),
    'password': fields.String(required=True, default="any2017")
})

login_model = ns.model('login', {
    'email': fields.String(required=True, default="username@gmail.com"),
    'password': fields.String(required=True, default="any@2017")
})

shoppinglist_model = ns.model('ShoppingList', {
    'name': fields.String(required=True, default="shoppinglist"),
    'description': fields.String(required=True, default="shopping description")
})

user_model = ns.model('Model', {
    'id':fields.Integer(default='your id'),
    'username': fields.String(default="username"),
    'email': fields.String(default="user@example.com"),
    'created_on':fields.DateTime
})

update_shoppinglist_model = ns.model('UpdateShoppingList', {
    'name': fields.String(required=True, default="updated shoppinglist"),
    'description': fields.String(required=True, default="updated shopping description")
})

add_item_model = ns.model('Items', {
    'name':fields.String(required=True, default="name"),
    'price':fields.String(required=True, default="price"),
    'quantity':fields.String(default="quantity"),
    'shoppinglist_id':fields.String(default="1")
})

