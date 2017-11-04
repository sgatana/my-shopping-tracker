from flask import g

from app import db
from app.Api_models.users import User, ShoppingList


def register_user(user):
    username = user.get('username')
    email = user.get('email')
    password = user.get('password')
    users = User(username, email, password)
    db.session.add(users)
    db.session.commit()


def add_shopping_list(data):
    name = data.get('name')
    desc = data.get('description')
    # revisit this part
    owner = g.user
    shopping_list=ShoppingList(name, desc, owner)
    db.session.add(shopping_list)
    db.session.commit()



























