from datetime import datetime
from app import db


class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    price = db.Column(db.Float())
    quantity = db.Column(db.Integer())
    shoppinglist_id = db.Column(db.Integer, db.ForeignKey('shoppinglists.id'))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    modified_on = db.Column(db.DateTime(), default=datetime.utcnow,
                            onupdate=datetime.utcnow)

    def __init__(self, name, price, quantity, shoppinglist, owner_id):
        self.name = name
        self.price = price
        self.quantity = quantity
        self.shoppinglist_id = shoppinglist.id
        self.owner_id = owner_id

