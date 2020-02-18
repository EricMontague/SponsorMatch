"""This module contains various configuration classes
to be used by the application.
"""


import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base class for application configuration"""

    # stored in a .flaskenv file
    SECRET_KEY = os.environ.get("SECRET KEY", "hard to guess string")
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in ["true", "on", "1"]
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_SUBJECT_PREFIX = "[SponsorMatch]"
    MAIL_SENDER = "montaguepython55@gmail.com"
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    EVENTS_PER_PAGE =  12
    UPLOADED_IMAGES_DEST = os.environ.get(
        "UPLOADS_URL", 
        os.path.join(basedir, "app/static/images")
    )
    # UPLOADED_IMAGES_DENY = []

class DevelopmentConfig(Config):
    """Class to setup the development configuration for the application"""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DEV_DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "data-dev.sqlite")
    # "mysql://root@localhost/sponsormatch-dev"


class TestingConfig(Config):
    """Class to setup the testing configuration for the application"""

    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL") or "sqlite://"


class ProductionConfig(Config):
    """Class to setop the production configuration for the application"""

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "data.sqlite")


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
