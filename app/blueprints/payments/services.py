"""This module contains functions that abstract away operations for
the payment blueprint.
"""
import uuid
from datetime import datetime
from http import HTTPStatus
from app.models import Event, Sponsorship, Package


class OutOfStock(Exception):
    pass


def validate_checkout_success(data, current_user, user_session):
    if not data:
        return {"message": "Request missing JSON body", "code": HTTPStatus.BAD_REQUEST}

    if "eventId" not in data:
        return {"message": "Missing 'eventId' field", "code": HTTPStatus.BAD_REQUEST}
    event = Event.query.get_or_404(int(data["eventId"]))
    if user_session.get(f"PENDING_ORDER#{current_user.id}#{event.id}") is None:
        {
            "message": "User has no pending orders for this event",
            "code": HTTPStatus.BAD_REQUEST,
        }
    return {}


def process_order(orders, db_session):
    for order in orders:
        purchased_package = Package.query.get(order["package_id"])
        if purchased_package.available_packages == 0:  # out of stock
            db_session.rollback()
            raise OutOfStock("The package you attempted to purchase is sold out.")
        order["confirmation_code"] = str(uuid.uuid4())
        order["timestamp"] = datetime.now()
        sponsorship = Sponsorship.create(**order)
        purchased_package.num_purchased += 1
    db_session.commit()
