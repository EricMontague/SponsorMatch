import os
from flask import render_template, redirect, url_for, flash, session, abort
from flask_login import current_user, login_required
from ..models import User, Permission
from ..email import send_email
from .. import db
from .forms import ChangePasswordForm, ChangeEmailForm, CloseAccountForm
from . import settings
from ..main.forms import EditProfileForm
from ..decorators import permission_required


@settings.route("/account_information", methods=["GET", "POST"])
@login_required
def account_information():
    """Return a page that let's the user edit their account information."""
    title = "Account Information"
    heading = title
    button_classes = "btn btn-primary"
    form = EditProfileForm(current_user)
    del form.about
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.company = form.company.data
        current_user.job_title = form.job_title.data
        current_user.website = form.website.data
        db.session.commit()
        flash("Your account information has been successfully updated.")
        return redirect(url_for("settings.account_information"))
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name
    form.company.data = current_user.company
    form.job_title.data = current_user.job_title
    form.website.data = current_user.website
    return render_template(
        "settings/settings.html", 
        form=form,
        title=title,
        heading=heading,
        button_classes=button_classes
    )


@settings.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """View function that renders the page to allow a user to
    change their password
    """
    title = "Change Your Password"
    heading = title
    button_classes = "btn btn-primary"
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            flash("Your password has been successfully changed.")
            return redirect(url_for("main.index"))
        else:
            flash("You entered an invalid password.")
    return render_template(
        "settings/settings.html", 
        form=form,
        title=title,
        heading=heading,
        button_classes=button_classes
    )


@settings.route("/change_email", methods=["GET", "POST"])
@login_required
def change_email():
    """View function that reners a page to allow a user to
    change their email
    """
    title = "Change Your Password"
    heading = title
    button_classes = "btn btn-primary"
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_change_email_token(new_email)
            send_email(
                new_email,
                "Change Email Address",
                "settings/email/confirm_email_change",
                user=current_user,
                token=token,
            )
            flash(
                "An email with instructions on how to change your email has been sent to you."
            )
            session["email_change_request"] = True
            return redirect(url_for("main.index"))
        else:
            flash("You entered an invalid password.")
    return render_template(
        "settings/settings.html", 
        form=form,
        title=title,
        heading=heading,
        button_classes=button_classes
    )


@settings.route("/confirm_email_change/<token>", methods=["GET"])
@login_required
def confirm_email_change(token):
    """View function to confirm the token sent to the user to change their email"""
    #used so that only a user who actually submitted an email change request
    #can access this route
    if session.get("email_change_request"):
        if current_user.change_email(token):
            db.session.commit()
            session["email_change_request"] = False
            flash("Your email address has been successfully updated!")
        else:
            flash("Your email address change was unsuccessful.")
    return redirect(url_for("main.index"))


@settings.route("/close_account", methods=["GET", "POST"])
@login_required
def close_account():
    """View function to render the page that allows a user to
    close their account
    """
    title = "Close Your Account"
    heading = title
    button_classes = "btn btn-danger"
    message = 'Please enter "CLOSE" in the field below to confirm the closing of your account.'
    form = CloseAccountForm()
    if form.validate_on_submit():
        # user = current_user._get_current_object()
        db.session.delete(current_user)
        db.session.commit()
        flash("Your account has been closed.")
        return redirect(url_for("main.index"))
    return render_template(
        "settings/settings.html", 
        form=form,
        title=title,
        heading=heading,
        button_classes=button_classes,
        message=message
    )



