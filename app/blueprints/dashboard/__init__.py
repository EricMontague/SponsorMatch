"""This package contains forms and views for the dashboard blueprint."""


from flask import Blueprint


dashboard = Blueprint("dashboard", __name__)


from app.blueprints.dashboard import views
