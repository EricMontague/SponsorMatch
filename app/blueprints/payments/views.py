"""This module contains view functions for the payments blueprint."""


from http import HTTPStatus
from flask import (
    current_app,
    jsonify,
    url_for,
    redirect,
    request,
    render_template,
    flash,
    session,
)
from app.extensions import db
from sqlalchemy import exc
from app.blueprints.payments import payments, services
from flask_login import login_required, current_user
from app.common import permission_required
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
    if session.get(f"PENDING_ORDER#{current_user.id}#{event_id}") is None:
        return redirect(url_for("main.index"))
    flash(
        "Please note: Navigating away from or refreshing this page will cancel your purchase.",
        "danger",
    )
    return render_template(
        "payments/checkout.html", event=event, publishable_key=publishable_key,
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
    data = services.validate_checkout_success(request.json, current_user, session)
    if data:
        return jsonify(data), HTTPStatus.BAD_REQUEST
    order_key = f"PENDING_ORDER#{current_user.id}#{request.json['eventId']}"
    try:
        services.process_order(session[order_key], db.session)
    except services.OutOfStock as err:
        return (
            {"message": str(err), "code": HTTPStatus.BAD_REQUEST},
            HTTPStatus.BAD_REQUEST,
        )
    db.session.commit()
    return (
        jsonify(
            {
                "message": "Your purchase was successful. A confirmation email was sent to you.",
                "code": HTTPStatus.CREATED,
            }
        ),
        HTTPStatus.CREATED,
    )

