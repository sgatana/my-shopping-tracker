import datetime
from app import db


class BlacklistToken(db.Model):
    """
    Token model for storing JWT token
    """
    __tablename__ = 'blacklist_tokens'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(255), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    @staticmethod
    def check_blacklist(token):
        # check whether auth token has been blacklisted
        response = BlacklistToken.query.filter_by(token=str(token)).first()
        if response:
            return True
        else:
            return False