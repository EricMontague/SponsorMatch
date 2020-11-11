"""This module contains view functions for the payments blueprint."""

import uuid
from datetime import datetime
from http import HTTPStatus
from flask import (
    current_app,
    jsonify,
    url_for,
    redirect,
    request,
    render_template,
    flash,
)
from app.extensions import db
from app.blueprints.payments import payments
from flask_login import login_required, current_user
from app.helpers import permission_required
from app.models import Permission, Event




@payments.route("/<int:event_id>/checkout", methods=["GET", "POST"])
@login_required
@permission_required(Permission.SPONSOR_EVENT)
def checkout(event_id):
    """Return a page that allows the sponsor to complete their
    purchases of the package(s).
    """
    event = Event.query.get_or_404(event_id)
    publishable_key = current_app.config["STRIPE_PUBLISHABLE_KEY"]
    sponsorships = current_user.pending_sponsorships(event_id)
    if sponsorships == []:
        return redirect(url_for("main.index"))
    flash(
        "Please note: Navigating away from or refreshing this page will cancel your purchase.",
        "danger",
    )
    return render_template(
        "payments/checkout.html",
        event=event,
        sponsorships=sponsorships,
        publishable_key=publishable_key
    )


@payments.route("/create-payment-intent", methods=["POST"])
@login_required
@permission_required(Permission.SPONSOR_EVENT)
def create_payment_intent():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Request missing JSON body"}), HTTPStatus.BAD_REQUEST
    if "orderTotal" not in json_data:
        return jsonify({"error": "Missing 'order_total' field"}), HTTPStatus.BAD_REQUEST
    try:
        intent = current_app.stripe.PaymentIntent.create(
            amount=json_data["orderTotal"], currency="usd"
        )
        return jsonify({"clientSecret": intent["client_secret"]}), HTTPStatus.CREATED
    except Exception as err:
        return jsonify({"error": str(err)}), HTTPStatus.BAD_REQUEST


@payments.route("checkout-success", methods=["POST"])
@login_required
@permission_required(Permission.SPONSOR_EVENT)
def checkout_success():
    """Route to handle updating the database after a successful payment."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "Request missing JSON body", "code": HTTPStatus.BAD_REQUEST}), HTTPStatus.BAD_REQUEST
    if "eventId" not in json_data:
        return jsonify({"message": "Missing 'eventId' field", "code": HTTPStatus.BAD_REQUEST}), HTTPStatus.BAD_REQUEST
    event = Event.query.get_or_404(int(json_data["eventId"]))
    sponsorships = current_user.pending_sponsorships(int(json_data["eventId"]))
    if sponsorships == []:  # user has no pending deals for this event
        return jsonify({"message": "User has not pending sponsorships for this event", "code": HTTPStatus.BAD_REQUEST}), HTTPStatus.BAD_REQUEST
    
    confirmation_code = str(uuid.uuid4())
    for sponsorship in sponsorships:
        sponsorship.confirmation_code = confirmation_code
        sponsorship.timestamp = datetime.now()
        sponsorship.package.num_purchased += 1
        if (
            sponsorship.package.available_packages
            - sponsorship.package.num_purchased
            < 0
        ):  # out of stock
            db.session.rollback()
            return jsonify({"message": "The package you attempted to purchase is sold out.", "code": HTTPStatus.BAD_REQUEST}), HTTPStatus.BAD_REQUEST
    db.session.commit()
    return jsonify({"message":"Your purchase was successful. A confirmation email was sent to you.", "code": HTTPStatus.CREATED }), HTTPStatus.CREATED


@payments.route("/<int:id>/cancel-purchase", methods=["POST"])
@login_required
@permission_required(Permission.SPONSOR_EVENT)
def cancel_purchase(id):
    """Function to be activated when a user navigates away from
    the purchase page before completing their purchase. Delete
    the appropriate sponsorship objects from the database.
    """
    event = Event.query.get_or_404(id)
    user = current_user._get_current_object()
    sponsorships = [
        sponsorship
        for sponsorship in user.sponsorships
        if sponsorship.event_id == event.id and sponsorship.is_pending()
    ]
    if sponsorships != []:
        for sponsorship in sponsorships:
            try:
                db.session.delete(sponsorship)
            except exc.IntegrityError as err:
                db.session.rollback()
                abort(500)
        db.session.commit()
    return redirect(url_for("dashboard.sponsorships_dashboard", status="all"))
    



