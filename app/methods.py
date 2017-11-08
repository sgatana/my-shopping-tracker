from flask import g

from app import db
from app.Api_models.users import User, ShoppingList
from app.Api_models.item import Item


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
    owner = g.user
    shopping_list=ShoppingList(name, desc, owner)
    db.session.add(shopping_list)
    db.session.commit()


def add_item(name, price, quantity, shoppinglist, owner_id):
    item=Item(name=name, price=price, quantity=quantity, shoppinglist=shoppinglist, owner_id=owner_id)
    check_item=Item.query.filter_by(name=name).filter_by(shoppinglist_id=shoppinglist.id).first()
    if not check_item:
        db.session.add(item)
        db.session.commit()
        return True
    else:
        return False





























