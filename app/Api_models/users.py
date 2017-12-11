import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.Api_models.shoppinglist import ShoppingList
import jwt
from flask import current_app
from app.Api_models.logout import BlacklistToken


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    email = db.Column(db.String(255), unique=True, index=True)
    password = db.Column(db.String(104))
    shopping_lists = db.relationship(ShoppingList, backref='owner', lazy='dynamic')
    items = db.relationship(ShoppingList, backref='items_owner', lazy='dynamic')
    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    date_modified = db.Column(db.DateTime, default=datetime.datetime.utcnow,
                              onupdate=datetime.datetime.utcnow)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)

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

    def encode_auth_token(self, user_id):
        """
        Generate the auth token
        :param user_id:
        :return:
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                current_app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """Decodes the authentication token"""

        try:
            payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                return 'token is blacklisted. Please try again'
            else:
                return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Sorry your token expired, please log in again!'
        except jwt.InvalidTokenError:
            return 'Token invalid, please login again.'


