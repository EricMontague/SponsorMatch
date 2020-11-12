"""This module contains view functions for the users blueprint."""


import os
from flask_login import login_required, current_user
from app.blueprints.users import users
from app.extensions import db, images
from flask import (
    render_template,
    url_for,
    redirect,
    flash,
    request,
    abort,
    current_app,
    session
)
from app.models import (
    User,
    Role,
    Event,
    Permission,
    Sponsorship,
    EventStatus,
    SponsorshipStatus
)
from app.blueprints.events.forms import UploadImag-eForm, RemoveImageForm
from app.blueprints.users.forms import EditProfileForm, EditProfileAdminForm
from app.helpers import admin_required



@users.route("/<company>")
def user_profile(company):
    """Return a page that allows someone to view a user's profile."""
    page = request.args.get("page", 1, type=int)
    past = request.args.get("past", 0, type=int)
    user_type = "sponsor"
    if user.can(Permission.CREATE_EVENT) or user.is_administrator():
        user_type = "event_organizer"
    profile_data = services.get_event_organizer_profile_data(
        company,
        user_type, 
        page, 
        current_app.config["EVENTS_PER_PAGE"], 
        past
    )
    return render_template(
        "users/user_profile.html",
        tab=profile_data["tab"],
        user=profile_data["user"],
        events=profile_data["pagination"].items,
        pagination=profile_data["pagination"],
        profile_photo=profile_data["user"].profile_photo,
    )


@users.route("/<int:id>/events/<status>")
def user_events_by_status(id, status):
    """Return a list of events organized by a given user."""
    if status not in (EventStatus.LIVE, EventStatus.PAST):
        abort(404)
    user = User.query.get_or_404(id)
    events = user.get_events_by_status(status)
    return render_template("events/_events.html", events=events)


@users.route("/<int:id>/sponsorships/<status>")
def user_sponsored_events_by_status(id, status):
    """Return a list of events sponsored by a given user."""
    if status not in (SponsorshipStatus.PAST, SponsorshipStatus.CURRENT):
        abort(404)
    user = User.query.get_or_404(id)
    sponsorships = user.get_sponsorships_by_status(status)
    events = [sponsorship.event for sponsorship in sponsorships]
    return render_template("events/_events.html", events=events)


@users.route("/edit-profile/add-photo", methods=["POST"])
@login_required
def add_profile_photo():
    """View function to upload a user's profile photo."""
    form = UploadImageForm()
    if form.validate_on_submit():
        try:
            services.upload_user_profile_photo(current_user, form.image.data, images, os)
        except services.PhotoUploadError as err:
            flash(str(err), "danger")
            return redirect(url_for("users.edit_profile"))
        db.session.commit()
        flash("Your profile photo was successfully uploaded.", "success")
    else:
        session["image_form_errors"] = form.image.errors
    return redirect(url_for("users.edit_profile"))


@users.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    """View function that renders the page to allow a user to update
    their contact information"""
    admin_route = False
    upload_image_form = UploadImageForm()
    upload_image_form.image.errors = session.pop("image_form_errors", [])
    remove_image_form = RemoveImageForm()
    profile_form = EditProfileForm(user)
    if profile_form.validate_on_submit():
        current_user.populate_from_form(form)
        db.session.add(current_user)
        db.session.commit()
        flash("Your profile information has been successfully updated.", "success")
        return redirect(url_for("users.edit_profile"))
    profile_form.populate_from_model(current_user)
    return render_template(
        "users/edit_profile.html",
        profile_form=profile_form,
        upload_image_form=upload_image_form,
        remove_image_form=remove_image_form,
        user=user,
        admin_route=admin_route,
        profile_photo=current_user.profile_photo,
    )


@users.route("/edit-profile/<int:id>/add-photo", methods=["POST"])
@login_required
@admin_required
def add_profile_photo_admin(id):
    """View function to upload a user's profile photo."""
    user = User.query.get_or_404(id)
    form = UploadImageForm()
    if form.validate_on_submit():
        try:
            services.upload_user_profile_photo(current_user, form.image.data, images, os)
        except services.PhotoUploadError as err:
            flash(str(err), "danger")
            return redirect(url_for("users.edit_profile"))
        db.session.commit()
        flash("Photo was successfully uploaded.", "success")
    else:
        session["image_form_errors"] = form.image.errors
    return redirect(url_for("users.edit_profile_admin", id=id))


@users.route("/images/<string:filename>/delete", methods=["POST"])
@login_required
def delete_image(filename):
    """View function to delete a profile image."""
    referrer = request.referrer
    path = "/Users/ericmontague/sponsormatch/app/static/images/" + filename
    try:
        services.delete_user_profile_photo(path, current_user, os)
    except services.PhotoNotFoundError as err:
        flash(str(err), "danger")
        abort(404)
    db.session.commit()
    flash("Your profile photo was successfully deleted.", "success")
    return redirect(referrer)
    

@users.route("/edit-profile/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_profile_admin(id):
    """Return a view that allows the admin to edit a user's information."""
    user = User.query.get_or_404(id)
    upload_image_form = UploadImageForm()
    upload_image_form.image.errors = session.pop("image_form_errors", [])
    remove_image_form = RemoveImageForm()
    profile_form = EditProfileAdminForm(user)
    if profile_form.validate_on_submit():
        form_data = form.data
        form_data["role"] = Role.query.get(profile_form.role.data)
        user.populate_from_form(form_data)
        db.session.commit()
        flash("The user's profile information has been successfully updated.", "success")
        return redirect(url_for("users.edit_profile_admin", id=user.id))
    profile_form.populate_from_model(user)
    return render_template(
        "users/edit_profile.html",
        profile_form=profile_form,
        upload_image_form=upload_image_form,
        remove_image_form=remove_image_form,
        profile_photo=user.profile_photo,
        user=user,
        admin_route=True,
    )
