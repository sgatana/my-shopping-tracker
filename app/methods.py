from app import db
from app.Api_models.users import User
def register_user(user):
    username = user.get('username')
    email = user.get('email')
    password = user.get('password')
    users = User(username, email, password)
    db.session.add(users)
    db.session.commit()


def delete_item(item):
    db.session.delete(item)
    db.session.commit()


def update_shopping_list(shoppinglist, name, description):
    shoppinglist.description = description
    shoppinglist.name = name
    db.session.commit()


def update_item(item, name, price, quantity):
    item.name = name
    item.price = price
    item.quantity=quantity
    db.session.commit()



























