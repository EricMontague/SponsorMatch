"""This package contains forms and view functions for the events blueprint."""


from flask import Blueprint


events = Blueprint("events", __name__)


from events import views
