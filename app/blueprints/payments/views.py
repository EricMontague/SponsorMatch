"""This module contains view functions for the payments blueprint."""

from flask import current_app, jsonify, url_for, redirect, request, render_template
from app.blueprints.payments import payments
from flask_login import login_required, current_user


@payments.route("/subscription")
@login_required
def subscription():
    """Return the template for the page that allows the user to enter 
    their payment information for a subscription.
    """
    if (
        current_user.is_anonymous
        or current_user.has_paid
        or current_user.role.name != "Event Organizer"
    ):
        return redirect(url_for("main.index"))
    publishable_key = current_app.config["STRIPE_PUBLISHABLE_KEY"]
    return render_template(
        "payments/subscription.html", publishable_key=publishable_key
    )


@payments.route("/subscription-sucess")
@login_required
def subscription_success():
    if (
        current_user.is_anonymous
        or current_user.has_paid
        or current_user.role.name != "Event Organizer"
    ):
        return redirect(url_for("main.index"))
    return render_template("payments/subscription_success.html")


@payments.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    session = current_app.stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "Purchase Subscription"},
                    "unit_amount": current_app.config["SUBSCRIPTION_AMOUNT"],
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url="http://localhost:5000/payments/subscription-success",
        cancel_url="http://localhost:5000/payments/subscription",
    )

    return jsonify(id=session.id)
