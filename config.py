import os


class Config(object):
    """
    Common configurations
    """

    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "hellofromtheotherside"


class DevelopmentConfig(Config):
    """
    Development configurations
    """

    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:steve012@localhost/flask_api"
    DEBUG = True
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    """Configurations for Testing, with a separate test database."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:steve012@localhost/test_db"


class ProductionConfig(Config):
    """
    Production configurations
    """
    DEBUG = False

app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}