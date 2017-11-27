from flask import g, jsonify

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


def delete_item(item):
    db.session.delete(item)
    db.session.commit()


def update_shopping_list(shoppinglist, name, description):
    if description is not None:
        shoppinglist.description = description
    if name is not None:
        shoppinglist.name = name
    db.session.commit()


def update_item(item, name, price, quantity):
    if name is not None:
        item.name = name
    if price is not None:
        item.price = price
    if quantity is not None:
        item.quantity=quantity
    db.session.commit()



























