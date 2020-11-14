"""This module contains view functions for the settings blueprint."""


import os
from flask import render_template, redirect, url_for, flash, session, abort
from flask_login import current_user, login_required
from app.models import User, Permission
from app.common import send_email
from app.extensions import db
from app.blueprints.settings import settings
from app.blueprints.settings.forms import (
    ChangePasswordForm,
    ChangeEmailForm,
    CloseAccountForm,
)
from app.blueprints.users.forms import EditProfileForm
from app.common import permission_required
from app.blueprints.settings import services


@settings.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    """View function that renders the page to allow a user to
    change their password
    """
    title = "Change Your Password"
    heading = title
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            flash("Your password has been successfully changed.", "success")
            return redirect(url_for("settings.change_password"))
        else:
            flash("You entered an invalid password.", "danger")
    return render_template(
        "settings/settings.html",
        form=form,
        title=title,
        heading=heading,
        endpoint="settings.change_password",
    )


@settings.route("/change-email", methods=["GET", "POST"])
@login_required
def change_email():
    """View function that reners a page to allow a user to
    change their email
    """
    title = "Change Your Email"
    heading = title
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            services.change_email_request(current_user, form.email.data)
            flash(
                "An email with instructions on how to change your email has been sent to you.",
                "info",
            )
            session["email_change_request_initiated"] = True
            return redirect(url_for("main.index"))
        else:
            flash("You entered an invalid passowrd", "danger")
            

    return render_template(
        "settings/settings.html",
        form=form,
        title=title,
        heading=heading,
        endpoint="settings.change_email",
    )


@settings.route("/confirm-email-change/<token>", methods=["GET"])
@login_required
def confirm_email_change(token):
    """View function to confirm the token sent to the user to change their email"""
    # used so that only a user who actually submitted an email change request
    # can access this route
    if session.get("email_change_request_initiated"):
        if current_user.change_email(token):
            db.session.commit()
            session["email_change_request_initiated"] = False
            flash("Your email address has been successfully updated!", "success")
        else:
            flash("Your email address change was unsuccessful.", "danger")
    return redirect(url_for("main.index"))


@settings.route("/close-account", methods=["GET", "POST"])
@login_required
def close_account():
    """View function to render the page that allows a user to
    close their account
    """
    title = "Close Your Account"
    heading = title
    message = 'Please enter "CLOSE" in the field below to confirm the closing of your account.'
    form = CloseAccountForm()
    if form.validate_on_submit():
        db.session.delete(current_user)
        db.session.commit()
        flash("Your account has been closed.", "info")
        return redirect(url_for("main.index"))
    return render_template(
        "settings/settings.html",
        form=form,
        title=title,
        heading=heading,
        message=message,
        endpoint="settings.close_account",
    )
