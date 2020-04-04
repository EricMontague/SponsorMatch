import stripe
from flask import Flask
from elasticsearch import Elasticsearch
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from config import config


bootstrap = Bootstrap()
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
images = UploadSet("images", extensions=["jpg", "jpeg", "png"])
login_manager.login_view = "auth.login"


def register_blueprints(app):
    """Register blueprints with the application."""
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    from .settings import settings as settings_blueprint
    app.register_blueprint(settings_blueprint, url_prefix="/settings")


def register_extensions(app):
    """Register the application instance with the extensions."""
    bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    configure_uploads(app, images)
    patch_request_class(app)

    # redirect requests sent to http to secure https when deployed on Heroku
    if app.config["SSL_REDIRECT"]:
        from flask_sslify import SSLify
        sslify = SSLify(app)


def add_attributes(app):
    """Add attributes to the application instance."""
    stripe.api_key = app.config["STRIPE_SECRET_KEY"]
    app.stripe = stripe

    # if statement is so that I have the option pf
    # not having Elasticsearch run during testing
    if app.config["ELASTICSEARCH_URL"]:
        app.elasticsearch = Elasticsearch([app.config["ELASTICSEARCH_URL"]])


def create_app(config_name):
    """Return an instance of the application
	after configuration and initializing it with
	the necessary Flask extensions.
	"""
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config[config_name])
    register_extensions(app)
    add_attributes(app)
    register_blueprints(app)
    return app

