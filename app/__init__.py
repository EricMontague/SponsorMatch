import stripe
from flask import Flask
from app.extensions import (
    bootstrap,
    db,
    mail,
    login_manager,
    images,
    configure_uploads,
    patch_request_class,
)
from app.search import FlaskSQLAlchemyMiddleware, ElasticsearchClient
from config import CONFIG_MAPPER
import os

def register_blueprints(app):
    """Register blueprints with the application."""
    from app.blueprints import main as main_blueprint
    from app.blueprints import auth as auth_blueprint
    from app.blueprints import settings as settings_blueprint
    from app.blueprints import users as users_blueprint
    from app.blueprints import dashboard as dashboard_blueprint
    from app.blueprints import events as events_blueprint
    from app.blueprints import payments as payments_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix="/auth")
    app.register_blueprint(settings_blueprint, url_prefix="/settings")
    app.register_blueprint(users_blueprint, url_prefix="/users")
    app.register_blueprint(dashboard_blueprint, url_prefix="/dashboard")
    app.register_blueprint(events_blueprint, url_prefix="/events")
    app.register_blueprint(payments_blueprint, url_prefix="/payments")


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


def add_attributes(app, use_elasticsearch):
    """Add attributes to the application instance."""
    stripe.api_key = app.config["STRIPE_SECRET_KEY"]
    app.stripe = stripe

    if use_elasticsearch:
        elasticsearch_client = ElasticsearchClient(app.config["ELASTICSEARCH_URL"])
        sqlalchemy_search_middleware = FlaskSQLAlchemyMiddleware(elasticsearch_client, db)
        app.sqlalchemy_search_middleware = sqlalchemy_search_middleware
        db.event.listen(
            db.session, "before_commit", sqlalchemy_search_middleware.before_commit
        )
        db.event.listen(
            db.session, "after_commit", sqlalchemy_search_middleware.after_commit
        )


def create_app(config_name, use_elasticsearch):
    """Return an instance of the application
	after configuration and initializing it with
	the necessary Flask extensions.
	"""
    
    app = Flask(__name__.split(".")[0])
    app.config.from_object(CONFIG_MAPPER[config_name])
    register_extensions(app)
    add_attributes(app, use_elasticsearch)
    register_blueprints(app)
    return app

