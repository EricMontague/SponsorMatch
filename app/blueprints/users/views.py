"""This module contains view functions for the users blueprint."""


import os
from flask_login import login_required, current_user
from app.blueprints.users import users
from app.extensions import db
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
from app.blueprints.events.forms import UploadImageForm, RemoveImageForm
from app.blueprints.users.forms import EditProfileForm, EditProfileAdminForm
from app.helpers import admin_required



@users.route("/<company>")
def user_profile(company):
    """Return a page that allows someone to view a user's profile."""
    user = User.query.filter_by(company=company).first_or_404()
    page = request.args.get("page", 1, type=int)
    past = request.args.get("past", 0, type=int)
    profile_photo = user.profile_photo
    if user.can(Permission.CREATE_EVENT) or user.is_administrator():
        tab = "live_event"
        if past == 1:
            tab = "past_event"
            query = Event.query.filter(
                Event.user_id == user.id, Event.has_ended() == True
            )
        else:  # query live events
            query = Event.query.filter(
                Event.user_id == user.id, Event.is_ongoing() == True
            )
    else:  # user is a sponsor
        tab = "current_sponsorship"
        if past == 1:
            tab = "past_sponsorship"
            query = (
                Event.query.join(Sponsorship, Sponsorship.event_id == Event.id)
                .filter(Event.is_past() == True)
                .filter(
                    Sponsorship.sponsor_id == user.id, Sponsorship.is_pending() == False
                )
            )
        else:  # current sponsored events
            query = (
                Event.query.join(Sponsorship, Sponsorship.event_id == Event.id)
                .filter(Event.is_ongoing() == True)
                .filter(
                    Sponsorship.sponsor_id == user.id, Sponsorship.is_pending() == False
                )
            )

    pagination = query.paginate(
        page=page, per_page=current_app.config["EVENTS_PER_PAGE"], error_out=False
    )
    events = pagination.items
    return render_template(
        "users/user_profile.html",
        tab=tab,
        user=user,
        events=events,
        pagination=pagination,
        profile_photo=profile_photo,
    )


@users.route("/<int:id>/events/<status>")
def user_events(id, status):
    """Return a list of events organized by a given user."""
    user = User.query.get_or_404(id)
    if status == EventStatus.LIVE:
        events = [event for event in user.events if event.is_ongoing()]
    elif status == EventStatus.PAST:
        events = [event for event in user.events if event.has_ended()]
    else:
        abort(404)
    return render_template("_events.html", events=events)


@users.route("/<int:id>/sponsorships/<status>")
def user_sponsorships(id, status):
    """Return a list of events sponsored by a given user."""
    user = User.query.get_or_404(id)
    if status == SponsorshipStatus.CURRENT:
        events = [
            sponsorship.event
            for sponsorship in user.sponsorships
            if not sponsorship.is_pending() and sponsorship.is_current()
        ]
    elif status == SponsorshipStatus.PAST:
        events = [
            sponsorship.event
            for sponsorship in user.sponsorships
            if not sponsorship.is_pending() and sponsorship.is_past()
        ]
    else:
        abort(404)
    return render_template("_events.html", events=events)


@users.route("/edit-profile/add-photo", methods=["POST"])
@login_required
def add_profile_photo():
    """View function to upload a user's profile photo."""
    form = UploadImageForm()
    if form.validate_on_submit():
        filename = images.save(form.image.data)
        if current_user.profile_photo_path is not None:  # updating profile photo
            try:
                # remove current image in the image folder
                os.remove(current_user.profile_photo_path)
            except OSError:
                flash("Upload was unsuccessful, please try again.")
                return redirect(url_for("users.edit_profile"))
        current_user.profile_photo_path = images.path(filename)
        db.session.commit()
        flash("Your profile photo was successfully uploaded.")
    else:
        session["image_form_errors"] = form.image.errors
    return redirect(url_for("users.edit_profile"))


@users.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    """View function that renders the page to allow a user to update
    their contact information"""
    admin_route = False
    user = current_user._get_current_object()
    profile_photo = current_user.profile_photo
    upload_image_form = UploadImageForm()
    upload_image_form.image.errors = session.pop("image_form_errors", [])
    remove_image_form = RemoveImageForm()
    profile_form = EditProfileForm(user)
    if profile_form.validate_on_submit():
        current_user.first_name = profile_form.first_name.data
        current_user.last_name = profile_form.last_name.data
        current_user.company = profile_form.company.data
        current_user.about = profile_form.about.data
        current_user.job_title = profile_form.job_title.data
        current_user.website = profile_form.website.data
        db.session.add(current_user)
        db.session.commit()
        flash("Your profile information has been successfully updated.")
        return redirect(url_for("users.edit_profile"))
    # prefill form with the user's current information
    profile_form.first_name.data = current_user.first_name
    profile_form.last_name.data = current_user.last_name
    profile_form.company.data = current_user.company
    profile_form.about.data = current_user.about
    profile_form.job_title.data = current_user.job_title
    profile_form.website.data = current_user.website
    return render_template(
        "users/edit_profile.html",
        profile_form=profile_form,
        upload_image_form=upload_image_form,
        remove_image_form=remove_image_form,
        user=user,
        admin_route=admin_route,
        profile_photo=profile_photo,
    )


@users.route("/edit-profile/<int:id>/add-photo", methods=["POST"])
@login_required
@admin_required
def add_profile_photo_admin(id):
    """View function to upload a user's profile photo."""
    user = User.query.get_or_404(id)
    form = UploadImageForm()
    if form.validate_on_submit():
        filename = images.save(form.image.data)
        if user.profile_photo_path is not None:  # updating profile photo
            if os.path.exists(user.profile_photo_path):
                os.remove(user.profile_photo_path)
            else:
                flash("Upload was unsuccessful, please try again.")
                return redirect(url_for("users.edit_profile_admin", id=id))
        user.profile_photo_path = images.path(filename)
        db.session.commit()
        flash("Photo was successfully uploaded.")
    else:
        session["image_form_errors"] = form.image.errors
    return redirect(url_for("users.edit_profile_admin", id=id))


@users.route("/edit-profile/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_profile_admin(id):
    """Return a view that allows the admin to edit a user's information."""
    admin_route = True
    user = User.query.get_or_404(id)
    profile_photo = user.profile_photo
    upload_image_form = UploadImageForm()
    upload_image_form.image.errors = session.pop("image_form_errors", [])
    remove_image_form = RemoveImageForm()
    profile_form = EditProfileAdminForm(user)
    if profile_form.validate_on_submit():
        user.first_name = profile_form.first_name.data
        user.last_name = profile_form.last_name.data
        user.company = profile_form.company.data
        user.about = profile_form.about.data
        user.job_title = profile_form.job_title.data
        user.website = profile_form.website.data
        user.email = profile_form.email.data
        user.has_paid = profile_form.has_paid.data
        user.role = Role.query.get(profile_form.role.data)
        db.session.add(user)
        db.session.commit()
        flash("The user's profile information has been successfully updated.")
        return redirect(url_for("users.edit_profile_admin", id=user.id))
    profile_form.first_name.data = user.first_name
    profile_form.last_name.data = user.last_name
    profile_form.company.data = user.company
    profile_form.about.data = user.about
    profile_form.job_title.data = user.job_title
    profile_form.website.data = user.website
    profile_form.email.data = user.email
    profile_form.has_paid.data = user.has_paid
    profile_form.role.data = user.role.id
    return render_template(
        "users/edit_profile.html",
        profile_form=profile_form,
        upload_image_form=upload_image_form,
        remove_image_form=remove_image_form,
        profile_photo=profile_photo,
        user=user,
        admin_route=admin_route,
    )
