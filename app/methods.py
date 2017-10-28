from app import db
import sqlalchemy
from app.Api_models.users import User


def register_user(user):
    username=user.get('username')
    email=user.get('email')
    password=user.get('password')
    users=User(username, email, password)
    db.session.add(users)
    db.session.commit()

