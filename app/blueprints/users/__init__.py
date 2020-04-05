"""This package contains forms and views for the users blueprint."""


from flask import Blueprint


users = Blueprint("users", __name__)


from users import views
