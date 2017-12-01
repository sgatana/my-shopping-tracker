from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.Api_models.shoppinglist import ShoppingList
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from app import app_config


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    email = db.Column(db.String(255), unique=True, index=True)
    password = db.Column(db.String(104))
    confirm = db.Column(db.String(104))
    shopping_lists = db.relationship(ShoppingList, backref='owner', lazy='dynamic')
    items = db.relationship(ShoppingList, backref='items_owner', lazy='dynamic')
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    date_modified = db.Column(db.DateTime, default=datetime.utcnow,
                              onupdate=datetime.utcnow)

    def __init__(self, username, email, password, confirm):
        self.username = username
        self.email = email
        self.set_password(password)
        self.confirm=password

    def __repr__(self):
        """
         string representation that can be used for debugging
         and testing purposes.
        """
        return '<User %r>' % self.email

    def set_password(self, password):
        """
        Sets current users password as a password hash
        """
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def generate_auth_token(self, expiration=3600, config=""):
        s = Serializer(app_config[config].SECRET_KEY, expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token, config):
        s = Serializer(app_config[config].SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user