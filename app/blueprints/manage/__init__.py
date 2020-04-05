"""This package contains forms and views for the manage blueprint."""


from flask import Blueprint


manage = Blueprint("manage", __name__)


from manage import views
