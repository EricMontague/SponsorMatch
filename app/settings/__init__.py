"""This package contains all of the modules for the
account settings blueprint.

"""
from flask import Blueprint

settings = Blueprint("settings", __name__)

from . import views
