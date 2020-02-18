"""This package contains all modules
that deal with user authentication
"""

from flask import Blueprint


auth = Blueprint("auth", __name__)


from . import views
