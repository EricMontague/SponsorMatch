"""This package contains all forms and views for the 
settings blueprint.
"""


from flask import Blueprint


settings = Blueprint("settings", __name__)


from settings import views
