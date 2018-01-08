# third-party imports
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# local imports
from config import app_config

# db variable initialization
db = SQLAlchemy()

from app.api.v1 import ns, api, bp

api.add_namespace(ns, path='/v1')


def create_app(config_name):
    app = Flask(__name__)
    Migrate(app, db)
    app.config.from_object(app_config[config_name])
    db.init_app(app)
    app.register_blueprint(bp)
    return app
