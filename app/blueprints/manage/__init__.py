"""This package contains forms and views for the manage blueprint."""


from flask import Blueprint


manage = Blueprint("manage", __name__)


from app.blueprints.manage import views
