"""This module contains functions that serve to abstract operations
in event blueprint."""

from flask import url_for
from http import HTTPStatus
from app.models import Event, Package


def validate_order(id, data, user):
    """Validate the request parameters from the user for the
    place order route. Returns the packages the user requested
    if validation is successful, else it returns a dictionary
    containing an error message to show to the user.
    """
    event = Event.query.get_or_404(id)
    if not data:
        return {"message": "Request missing JSON body"}
    if "ids" not in data:
        return {"message": "'Ids' field missing from request"}
    packages = []
    for package_id in data["ids"]:
        package = Package.query.get_or_404(package_id)
        if user.has_purchased(package):
            return {
                "message": "You cannot purchase a package more than once",
                "url": url_for("events.event", id=event.id),
            }
        packages.append(package)
    return {"packages": packages}

