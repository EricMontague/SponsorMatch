"""This package contains forms and views for the auth blueprint."""

from flask import Blueprint


auth = Blueprint("auth", __name__)


from app.blueprints.auth import views
