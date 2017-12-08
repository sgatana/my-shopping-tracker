from datetime import datetime
from app import db
from app.Api_models.item import Item


class ShoppingList(db.Model):
    __tablename__ = "shoppinglists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255)) # add unique
    description = db.Column(db.String(255))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    items = db.relationship(Item, backref='shoppinglist', lazy='dynamic')
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    modified_on = db.Column(db.DateTime(), default=datetime.utcnow,
                            onupdate=datetime.utcnow)

    def __init__(self, name, description, owner):
        self.name = name
        self.description = description
        self.owner_id = owner

    def __repr__(self):
        """
         string representation that can be used for debugging
         and testing purposes.
        """
        return '<Shopping list %r> <owner %r>' % self.name % self.owner_id

    def save(self):
        db.session.add(self)
        db.session.commit()