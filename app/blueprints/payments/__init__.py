"""This package contains forms and view functions for the payments blueprint."""


from flask import Blueprint


payments = Blueprint("payments", __name__)


from app.blueprints.payments import views
