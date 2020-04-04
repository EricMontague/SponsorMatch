import os
import uuid
from datetime import datetime
from sqlalchemy import func, exc
from flask import (
    render_template,
    url_for,
    redirect,
    flash,
    request,
    abort,
    g,
    current_app,
    session,
    jsonify,
    make_response,
)
from flask_login import login_required, current_user
from . import main
from .forms import (
    CreateEventForm,
    EventDetailsForm,
    EventPackagesForm,
    UploadVideoForm,
    RemoveVideoForm,
    MultipleImageForm,
    DemographicsForm,
    UploadImageForm,
    RemoveImageForm,
    EditProfileForm,
    EditProfileAdminForm,
    ContactForm,
    AdvancedSearchForm,
    SearchForm,
    DropdownForm,
)
from ..email import send_email
from ..models import (
    User,
    Role,
    Image,
    ImageType,
    Event,
    EventType,
    EventCategory,
    Venue,
    Package,
    Video,
    Permission,
    Sponsorship,
    EventStatus,
    SponsorshipStatus,
)
from .. import db, images
from ..decorators import permission_required, admin_required


@main.route("/")
def index():
    """Return the home page of the application."""
    form = AdvancedSearchForm()
    near_you = False
    if current_user.is_authenticated:
        near_you = bool(request.cookies.get("near_you", ""))
    if near_you:
        query = current_user.nearby_events
    else:
        query = Event.query
    page = request.args.get("page", 1, type=int)
    pagination = query.filter(Event.is_ongoing() == True).paginate(
        page, per_page=current_app.config["EVENTS_PER_PAGE"], error_out=False
    )
    events = pagination.items
    return render_template(
        "index.html", events=events, form=form, pagination=pagination
    )


# need to add cookie functionality for homepage later
@main.route("/all")
@login_required
def show_all():
    """Remove near_you cookie from user's browser to an empty string"""
    response = make_response(redirect(url_for(".index")))
    response.set_cookie("near_you", "", max_age=30 * 24 * 60 * 60)  # 30 days
    return response


# need to add cookie functionality for homepage later
@main.route("/near_you")
@login_required
def near_you():
    """Set a near_you cookie in the user's browser"""
    response = make_response(redirect(url_for(".index")))
    response.set_cookie("near_you", "1", max_age=30 * 24 * 60 * 60)  # 30 days
    return response


@main.route("/", methods=["POST"])
def advanced_search():
    """View function to handle queries from the advanced search form
    on the home page."""
    endpoint = "main.advanced_search"
    form = AdvancedSearchForm()
    if form.validate_on_submit():
        page = request.args.get("page", 1, type=int)
        state = AdvancedSearchForm.choice_value(form.state.data, "STATES")
        
        query = (
            Event.query.join(Venue, Venue.id == Event.venue_id)
            .filter(Venue.state == state)
            .filter(
                func.Date(Event.start_datetime) >= form.start_date.data,
                func.Date(Event.start_datetime) <= form.end_date.data,
                Event.is_ongoing() == True,
            )
        )
        # user selected all categories an omitted city
        if form.category.data == 0 and form.city.data == "":
            pagination = query.paginate(
                page, per_page=current_app.config["EVENTS_PER_PAGE"], error_out=False
            )
        # user selected all categories, but typed in a specific city
        elif form.category.data == 0:
            pagination = query.filter(Venue.city == form.city.data).paginate(
                page, per_page=current_app.config["EVENTS_PER_PAGE"], error_out=False
            )
        # user selected a specific category, but omitted the city
        elif form.city.data == "":
            pagination = query.filter(
                Event.event_category_id == form.category.data
            ).paginate(
                page, per_page=current_app.config["EVENTS_PER_PAGE"], error_out=False
            )
        # user filled out the form with complete specificity
        else:
            pagination = (
                query.filter(Venue.city == form.city.data)
                .filter(Event.event_category_id == form.category.data)
                .paginate(
                    page,
                    per_page=current_app.config["EVENTS_PER_PAGE"],
                    error_out=False,
                )
            )
        events = pagination.items
        prev_url = None
        if pagination.has_prev:
            prev_url = url_for("main.search", page=pagination.prev_num)
        next_url = None
        if pagination.has_next:
            next_url = url_for("main.search", page=pagination.next_num)
        return render_template(
            "search.html", events=events, prev_url=prev_url, next_url=next_url
        )
    events = Event.query.filter(Event.is_ongoing() == True).all()
    return render_template("index.html", events=events, form=form)


@main.route("/search")
def search():
    """Return search results."""
    if not g.search_form.validate():
        return redirect("main.index")
    endpoint = "main.search"
    page = request.args.get("page", 1, type=int)
    events, total = Event.search(
        g.search_form.query.data, page, current_app.config["EVENTS_PER_PAGE"]
    )
    live_events = None
    if events:
        events = [event for event in events if event.is_ongoing()]
    prev_url = None
    if page > 1:
        prev_url = url_for("main.search", query=g.search_form.query.data, page=page - 1)
    next_url = None
    if total > page * current_app.config["EVENTS_PER_PAGE"]:
        next_url = url_for("main.search", query=g.search_form.query.data, page=page + 1)
    return render_template(
        "search.html",
        events=events,
        endpoint=endpoint,
        prev_url=prev_url,
        next_url=next_url,
    )


@main.route("/users/<company>")
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
        "main/users/user_profile.html",
        tab=tab,
        user=user,
        events=events,
        pagination=pagination,
        profile_photo=profile_photo,
    )


@main.route("/users/<int:id>/events/<status>")
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


@main.route("/users/<int:id>/sponsorships/<status>")
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


@main.route("/edit_profile/add_photo", methods=["POST"])
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
                return redirect(url_for("main.edit_profile"))
        current_user.profile_photo_path = images.path(filename)
        db.session.commit()
        flash("Your profile photo was successfully uploaded.")
    else:
        session["image_form_errors"] = form.image.errors
    return redirect(url_for("main.edit_profile"))


@main.route("/edit_profile", methods=["GET", "POST"])
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
        return redirect(url_for("main.edit_profile"))
    # prefill form with the user's current information
    profile_form.first_name.data = current_user.first_name
    profile_form.last_name.data = current_user.last_name
    profile_form.company.data = current_user.company
    profile_form.about.data = current_user.about
    profile_form.job_title.data = current_user.job_title
    profile_form.website.data = current_user.website
    return render_template(
        "main/users/edit_profile.html",
        profile_form=profile_form,
        upload_image_form=upload_image_form,
        remove_image_form=remove_image_form,
        user=user,
        admin_route=admin_route,
        profile_photo=profile_photo,
    )


@main.route("/edit_profile/<int:id>/add_photo", methods=["POST"])
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
                return redirect(url_for("main.edit_profile_admin", id=id))
        user.profile_photo_path = images.path(filename)
        db.session.commit()
        flash("Photo was successfully uploaded.")
    else:
        session["image_form_errors"] = form.image.errors
    return redirect(url_for("main.edit_profile_admin", id=id))


@main.route("/edit_profile/<int:id>", methods=["GET", "POST"])
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
        return redirect(url_for("main.edit_profile_admin", id=user.id))
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
        "main/users/edit_profile.html",
        profile_form=profile_form,
        upload_image_form=upload_image_form,
        remove_image_form=remove_image_form,
        profile_photo=profile_photo,
        user=user,
        admin_route=admin_route,
    )


@main.route("/events/create", methods=["GET", "POST"])
@login_required
@permission_required(Permission.CREATE_EVENT)
def create_event():
    """Render the view that allows a user to create an event"""
    event = None
    form = CreateEventForm()
    if form.validate_on_submit():
        venue = Venue.query.filter_by(address=form.address.data).first()
        if venue is None:  # venue not already in db, need to add it
            venue = Venue(
                name=form.venue_name.data,
                address=form.address.data,
                city=form.city.data,
                state=CreateEventForm.choice_value(form.state.data, "STATES"),
                zip_code=form.zip_code.data,
            )
        event_type = EventType.query.get(form.event_type.data)
        event_category = EventCategory.query.get(form.category.data)
        start_time = CreateEventForm.choice_value(form.start_time.data, "TIMES")
        end_time = CreateEventForm.choice_value(form.end_time.data, "TIMES")
        event = Event(
            title=form.title.data,
            start_datetime=datetime.combine(form.start_date.data, start_time),
            end_datetime=datetime.combine(form.end_date.data, end_time),
            venue=venue,
            event_type=event_type,
            event_category=event_category,
            user=current_user._get_current_object(),
        )
        db.session.add(event)
        db.session.commit()
        return redirect(url_for("main.event_details", id=event.id))
    return render_template("main/events/create_event.html", form=form, event=event)


@main.route("/events/<int:id>/basic_info", methods=["GET", "POST"])
@login_required
@permission_required(Permission.CREATE_EVENT)
def edit_basic_info(id):
    """Return the view that allows a user to edit an event's basic info."""
    form = CreateEventForm()
    form.submit.label.text = "Update Event"
    event = Event.query.get_or_404(id)
    if not current_user.is_organizer(event) and not current_user.is_administrator():
        return redirect(url_for("main.index"))
    if form.validate_on_submit():
        event.title = form.title.data
        event_type = EventType.query.get(form.event_type.data)
        event_category = EventCategory.query.get(form.category.data)
        event.venue.name = form.venue_name.data
        event.venue.address = form.address.data
        event.venue.city = form.city.data
        event.venue.state = CreateEventForm.choice_value(form.state.data, "STATES")
        event.venue.zip_code = form.zip_code.data

        start_time = CreateEventForm.choice_value(form.start_time.data, "TIMES")
        end_time = CreateEventForm.choice_value(form.end_time.data, "TIMES")

        event.start_datetime = datetime.combine(form.start_date.data, start_time)
        event.end_datetime = datetime.combine(form.end_date.data, end_time)
        db.session.commit()
        flash("Your changes were saved.")
        return redirect(url_for("main.edit_basic_info", id=id))
    venue = event.venue
    form.title.data = event.title
    form.event_type.data = event.event_type.id
    form.category.data = event.event_category.id
    form.venue_name.data = venue.name
    form.address.data = venue.address
    form.city.data = venue.city
    form.state.data = CreateEventForm.choice_id(venue.state, "STATES")
    form.zip_code.data = venue.zip_code
    form.start_date.data = event.start_date()
    form.end_date.data = event.end_date()
    form.start_time.data = CreateEventForm.choice_id(event.start_time(), "TIMES")
    form.end_time.data = CreateEventForm.choice_id(event.end_time(), "TIMES")
    return render_template("main/events/create_event.html", form=form, event=event)


@main.route("/events/<int:id>/event_details", methods=["GET", "POST"])
@login_required
@permission_required(Permission.CREATE_EVENT)
def event_details(id):
    """Render a page that allows the user to enter more details
    about the event.
    """
    details_form = EventDetailsForm()
    upload_image_form = UploadImageForm()
    remove_image_form = RemoveImageForm()
    details_form.submit.label.text = "Submit"
    event = Event.query.get_or_404(id)
    main_image_path = event.main_image

    if not current_user.is_organizer(event) and not current_user.is_administrator():
        return redirect(url_for("main.index"))

    if details_form.validate_on_submit():
        event.description = details_form.description.data
        event.pitch = details_form.pitch.data
        db.session.commit()
        flash("Update successful.")
        return redirect(url_for("main.event_details", id=event.id))
    # pre-fill fields
    details_form.description.data = event.description
    details_form.pitch.data = event.pitch
    return render_template(
        "main/events/event_details.html",
        details_form=details_form,
        upload_image_form=upload_image_form,
        remove_image_form=remove_image_form,
        main_image_path=main_image_path,
        event=event,
    )


@main.route("/event/<int:id>/add_image", methods=["POST"])
@login_required
@permission_required(Permission.CREATE_EVENT)
def add_event_image(id):
    """view function to add an image to the database."""
    form = UploadImageForm()
    event = Event.query.get_or_404(id)
    if not current_user.is_organizer(event) and not current_user.is_administrator():
        return redirect(url_for("main.index"))
    if form.validate_on_submit():
        filename = images.save(form.image.data)
        image_type = ImageType.query.filter_by(name="Main Event Image").first()
        image = Image(path=images.path(filename), image_type=image_type, event=event)
        db.session.add(image)
        db.session.commit()
        flash("Your image was successfully uploaded.")
        return redirect(url_for("main.event_details", id=id))
    return redirect(url_for("main.event_details", id=event.id))


@main.route("/images/<string:filename>/delete", methods=["POST"])
@login_required
def delete_image(filename):
    """View function to delete an image."""
    referrer = request.referrer
    path = "/Users/ericmontague/sponsormatch/app/static/images/" + filename
    if request.endpoint == "main.edit_profile_admin":
        user = User.query.filter_by(profile_photo_path=path).first_or_404()
    else:
        user = current_user._get_current_object()
    if path == user.profile_photo_path:
        if os.path.exists(path):
            os.remove(path)
        user.profile_photo_path = None
        db.session.commit()
        flash("Your profile photo was successfully deleted.")
    else:  # deleting an event image
        image = Image.query.filter_by(path=path).first_or_404()
        event = Event.query.get_or_404(image.event_id)
        if not current_user.is_organizer(event) and not current_user.is_administrator():
            return redirect(url_for("main.index"))
        db.session.delete(image)
        db.session.commit()
        flash("Your event image was successfully deleted.")
    return redirect(referrer)


@main.route("/events/<int:id>/demographics", methods=["GET", "POST"])
@login_required
@permission_required(Permission.CREATE_EVENT)
def demographics(id):
    """Return a page that allows the user to give details
    about who is attending the event.
    """
    form = DemographicsForm()
    event = Event.query.get_or_404(id)
    if not current_user.is_organizer(event) and not current_user.is_administrator():
        return redirect(url_for("main.index"))
    if form.validate_on_submit():
        if form.males.data + form.females.data != 100:
            flash("Sum of males and females must equal 100.")
        else:
            event.attendees = DemographicsForm.choice_value(
                form.attendees.data, "PEOPLE_RANGES"
            )
            distribution = str(form.males.data) + "-" + str(form.females.data)
            event.male_to_female = distribution
            db.session.commit()
            flash("Your information has been successfilly uploaded.")
            return redirect(url_for("main.demographics", id=id))
    if event.attendees:
        form.attendees.data = DemographicsForm.choice_id(
            event.attendees, "PEOPLE_RANGES"
        )
    else:
        form.attendees.data = 1
    if event.male_to_female:
        distribution = event.male_to_female.split("-")
        form.males.data = distribution[0]
        form.females.data = distribution[1]
    else:
        form.males.data = 0
        form.females.data = 0
    return render_template("main/events/demographics.html", form=form, event=event)


@main.route("/packages/<int:id>")
@login_required
def view_package(id):
    """Return the details regarding a package as a json object."""
    package = Package.query.get_or_404(id)
    return jsonify(
        {
            "price": float(package.price),
            "audience": package.audience,
            "description": package.description,
            "package_type": package.package_type,
        }
    )


@main.route("/events/<int:id>/packages", methods=["GET", "POST"])
@login_required
@permission_required(Permission.CREATE_EVENT)
def packages(id):
    """Render a page that allows the user to select the sponsorship
    packages that will go along with thier event.
    """
    form = EventPackagesForm()
    event = Event.query.get_or_404(id)
    packages = event.packages.all()
    if not current_user.is_organizer(event) and not current_user.is_administrator():
        return redirect(url_for("main.index"))
    if form.validate_on_submit():
        package = Package(
            name=form.name.data,
            price=form.price.data,
            audience=EventPackagesForm.choice_value(
                form.audience.data, "PEOPLE_RANGES"
            ),
            description=form.description.data,
            available_packages=form.available_packages.data,
            package_type=EventPackagesForm.choice_value(
                form.package_type.data, "PACKAGE_TYPES"
            ),
            event=event,
        )
        db.session.commit()
        return redirect(url_for("main.packages", id=id))
    return render_template(
        "main/events/packages.html", form=form, event=event, packages=packages
    )


@main.route(
    "/events/<int:event_id>/packages/<int:package_id>/edit", methods=["GET", "POST"]
)
@login_required
@permission_required(Permission.CREATE_EVENT)
def edit_package(event_id, package_id):
    """View function to add a package to an event in the database."""
    form = EventPackagesForm()
    event = Event.query.get_or_404(event_id)
    package = event.packages.filter(Package.id == package_id).first_or_404()
    if not current_user.is_organizer(event) and not current_user.is_administrator():
        return redirect(url_for("main.index"))
    if form.validate_on_submit():
        package.name = form.name.data
        package.price = form.price.data
        package.audience = EventPackagesForm.choice_value(
            form.audience.data, "PEOPLE_RANGES"
        )
        package.description = form.description.data
        package.available_packages = form.available_packages.data
        package.package_type = EventPackagesForm.choice_value(
            form.package_type.data, "PACKAGE_TYPES"
        )
        db.session.commit()
        flash("Package details were successfully updated.")
        return redirect(url_for("main.packages", id=event_id))
    packages = event.packages.all()
    form.name.data = package.name
    form.price.data = package.price
    form.audience.data = EventPackagesForm.choice_id(package.audience, "PEOPLE_RANGES")
    form.description.data = package.description
    form.available_packages.data = package.available_packages
    form.package_type.data = EventPackagesForm.choice_id(
        package.package_type, "PACKAGE_TYPES"
    )
    return render_template(
        "main/events/packages.html", form=form, event=event, packages=packages
    )


@main.route("/events/<int:event_id>/packages/<int:package_id>/delete", methods=["POST"])
@login_required
@permission_required(Permission.CREATE_EVENT)
def delete_package(event_id, package_id):
    """View function to be executed when a user wants to remove
    a sponsorship package from their event.
    """
    event = Event.query.get_or_404(event_id)
    if not current_user.is_organizer(event) and not current_user.is_administrator():
        return redirect(url_for("main.index"))
    package = event.packages.filter(Package.id == package_id).first_or_404()
    db.session.delete(package)
    db.session.commit()
    return jsonify({"url": url_for("main.packages", id=event.id)})


@main.route("/events/<int:id>/video", methods=["POST"])
@login_required
@permission_required(Permission.CREATE_EVENT)
def add_video(id):
    """Add a video to the database for an event."""
    event = Event.query.get_or_404(id)
    if not current_user.is_organizer(event) and not current_user.is_administrator():
        return redirect(url_for("main.index"))
    upload_video_form = UploadVideoForm()
    if upload_video_form.validate_on_submit():
        video = Video(
            url=UploadVideoForm.parse_url(upload_video_form.video_url.data), event=event
        )
        db.session.add(video)
        db.session.commit()
        flash("Your upload was successful.")
        return redirect(url_for("main.media", id=id))
    else:
        session["upload_video_form_errors"] = upload_video_form.video_url.errors
        session["video_url"] = upload_video_form.video_url.data
    return redirect(url_for("main.media", id=event.id))


@main.route("/events/<int:id>/misc_images", methods=["POST"])
@login_required
@permission_required(Permission.CREATE_EVENT)
def add_misc_images(id):
    """Add multiple images to the database for an event."""
    event = Event.query.get_or_404(id)
    if not current_user.is_organizer(event) and not current_user.is_administrator():
        return redirect(url_for("main.index"))
    image_form = MultipleImageForm()
    if image_form.validate_on_submit():
        image_type = ImageType.query.filter_by(name="Misc").first()
        for data in image_form.images.data:
            filename = images.save(data)
            image = Image(
                path=images.path(filename), image_type=image_type, event=event
            )
            db.session.add(image)
        db.session.commit()
        flash("Your upload was successful.")
        return redirect(url_for("main.media", id=id))
    else:
        session["image_form_errors"] = image_form.images.errors
    return redirect(url_for("main.media", id=event.id))


@main.route("/events/<int:id>/media", methods=["GET", "POST"])
@login_required
@permission_required(Permission.CREATE_EVENT)
def media(id):
    """Return a page that allows the user do at various forms of
    media to their event page."""
    upload_video_form = UploadVideoForm()
    upload_video_form.video_url.errors = session.pop("upload_video_form_errors", [])
    upload_video_form.video_url.data = session.pop("video_url", "")
    remove_video_form = RemoveVideoForm()
    image_form = MultipleImageForm()
    image_form.images.errors = session.pop("image_form_errors", [])
    remove_image_form = RemoveImageForm()
    event = Event.query.get_or_404(id)
    video = event.video
    misc_image_paths = event.misc_images
    if not current_user.is_organizer(event) and not current_user.is_administrator():
        return redirect(url_for("main.index"))
    return render_template(
        "main/events/media.html",
        upload_video_form=upload_video_form,
        remove_video_form=remove_video_form,
        image_form=image_form,
        remove_image_form=remove_image_form,
        video=video,
        misc_image_paths=misc_image_paths,
        event=event,
    )


@main.route("/events/<int:event_id>/videos/<int:video_id>/delete", methods=["POST"])
@login_required
@permission_required(Permission.CREATE_EVENT)
def delete_video(event_id, video_id):
    """View function to delete a video."""
    event = Event.query.get_or_404(event_id)
    if not current_user.is_organizer(event) and not current_user.is_administrator():
        return redirect(url_for("main.index"))
    video = Video.query.get_or_404(video_id)
    db.session.delete(video)
    db.session.commit()
    flash("Your video has been deleted.")
    return redirect(url_for("main.media", id=event_id))


@main.route("/events/<int:id>/publish", methods=["POST"])
@login_required
@permission_required(Permission.CREATE_EVENT)
def publish(id):
    """View function that is called when a user wants to publish their
    event.
    """
    event = Event.query.get_or_404(id)
    if (
        not current_user.is_organizer(event) and not current_user.is_administrator()
    ) or event.has_ended():
        return redirect(url_for("main.index"))
    if event.description is None or event.pitch is None:
        flash("You cannot publish an event without adding a description or pitch.")
        return redirect(url_for("main.event_details", id=event.id))
    packages = event.packages.all()
    if packages == []:
        flash("You cannot publish an event without adding any packages.")
        return redirect(url_for("main.packages", id=event.id))
    event.published = True
    db.session.commit()
    flash("Your event has been published.")
    return redirect(url_for("main.index"))


@main.route("/events/<int:id>", methods=["GET", "POST"])
def event(id):
    """Return the view that displays the event's information"""
    other_media = {}
    date_format = "%m/%d/%Y"
    time_format = "%I:%M %p"
    form = ContactForm()
    event = Event.query.get_or_404(id)
    venue = event.venue
    organizer = event.user
    image_path = event.main_image
    other_media["video"] = event.video
    other_media["misc_image_paths"] = event.misc_images
    packages = event.packages.all()
    if form.validate_on_submit():
        send_email(
            organizer.email,
            f"Event Inquiry - {form.subject.data}",
            "main/email/contact_organizer",
            organizer=organizer,
            form=form,
            event=event,
        )
        flash("Your email was sent to the event organizer.")
        return redirect(url_for("main.event", id=id))
    return render_template(
        "main/events/event.html",
        event=event,
        venue=venue,
        organizer=organizer,
        packages=packages,
        form=form,
        date_format=date_format,
        image_path=image_path,
        time_format=time_format,
        other_media=other_media,
    )


@main.route("/events/<int:id>/<tab>")
def event_tab(id, tab):
    """Return an html template with the appropriate content
    based on the tab clicked by the user on an event's page.
    """
    other_media = {}
    event = Event.query.get_or_404(id)
    image_path = event.main_image
    other_media["video"] = event.video
    other_media["misc_image_paths"] = event.misc_images
    if tab == "info":
        return render_template(
            "_event_page_content.html",
            event=event,
            image_path=image_path,
            other_media=other_media,
        )
    elif tab == "sponsors":
        users = set()
        for sponsorship in event.sponsorships:
            if not sponsorship.is_pending():
                users.add(sponsorship.sponsor)
        return render_template("_users.html", event=event, users=users)
    else:
        abort(404)


@main.route("/events/<int:id>/delete", methods=["POST"])
@login_required
@permission_required(Permission.CREATE_EVENT)
def delete_event(id):
    """View function to delete an event."""

    event = Event.query.get(id)
    if not current_user.is_organizer(event) and not current_user.is_administrator():
        return redirect(url_for("main.index"))
    db.session.delete(event)
    db.session.commit()
    return jsonify({"message": "Your event has been successfully deleted."})


@main.route("/events/<int:id>/save", methods=["POST"])
@login_required
@permission_required(Permission.SPONSOR_EVENT)
def save_event(id):
    """Route to allow a sponsor to save an event to their favorites list."""
    event = Event.query.get_or_404(id)
    if not current_user.has_saved(event):
        current_user.save(event)
        db.session.commit()
        return jsonify({"message": "Event added to your saved events list."})
    else:
        return jsonify({"message": "You have already saved this event."})


@main.route("/saved_events")
@login_required
@permission_required(Permission.SPONSOR_EVENT)
def saved_events():
    """Return a page where sponsors can view their list of saved events."""
    endpoint = "main.saved_events"
    events = current_user.saved_events.all()
    return render_template(
        "main/events/saved_events.html", events=events, endpoint=endpoint
    )


@main.route("/saved_events/<int:id>/delete", methods=["POST"])
@login_required
@permission_required(Permission.SPONSOR_EVENT)
def delete_saved_event(id):
    """Remove the given saved event from the user's saved events list."""
    event = Event.query.get_or_404(id)
    if current_user.has_saved(event):
        current_user.unsave(event)
        db.session.commit()
        return jsonify(
            {"message": "The event was removed from your saved events list."}
        )
    return redirect(url_for("main.index"))


# need to add ajax requests in template for this route
@main.route("/manage_events/<status>")
@login_required
@permission_required(Permission.CREATE_EVENT)
def manage_events(status):
    """Return a page that allows a user to see all of their events in 
    one place.
    """
    choices = [(1, "All"), (2, "Live"), (3, "Past"), (4, "Draft")]
    dropdown_form = DropdownForm(choices)
    user = current_user._get_current_object()
    if status == EventStatus.LIVE:
        events = [event for event in user.events if event.is_ongoing()]
    elif status == EventStatus.DRAFT:
        events = [event for event in user.events if event.is_draft()]
    elif status == EventStatus.PAST:
        events = [event for event in user.events if event.has_ended()]
    else:
        events = user.events.all()

    # set default value equal to status
    reverse_choices = {choice.lower(): number for number, choice in choices}
    dropdown_form.options.data = reverse_choices[status]
    return render_template(
        "main/events/manage_events.html",
        user=user,
        events=events,
        dropdown_form=dropdown_form,
        datetime=datetime,
    )


@main.route("/manage_sponsorships/<status>")
@login_required
@permission_required(Permission.SPONSOR_EVENT)
def manage_sponsorships(status):
    """return a page that allows a sponsor to view current
    and past sponsorships."""
    choices = [(1, "All"), (2, "Current"), (3, "Past")]
    dropdown_form = DropdownForm(choices)
    user = current_user._get_current_object()
    if status == SponsorshipStatus.CURRENT:
        sponsorships = [
            sponsorship
            for sponsorship in user.sponsorships
            if not sponsorship.is_pending() and sponsorship.is_current()
        ]
    elif status == SponsorshipStatus.PAST:
        sponsorships = [
            sponsorship
            for sponsorship in user.sponsorships
            if not sponsorship.is_pending() and sponsorship.is_past()
        ]
    else:
        sponsorships = [
            sponsorship
            for sponsorship in user.sponsorships
            if not sponsorship.is_pending()
        ]

    reverse_choices = {choice.lower(): number for number, choice in choices}
    dropdown_form.options.data = reverse_choices[status]
    return render_template(
        "main/events/manage_sponsorships.html",
        sponsorships=sponsorships,
        dropdown_form=dropdown_form,
    )


@main.route("/events/<int:id>/sponsorships", methods=["POST"])
@login_required
@permission_required(Permission.SPONSOR_EVENT)
def create_sponsorships(id):
    """Create sponsorship objects and add them to the database."""
    event = Event.query.get_or_404(id)
    user = current_user._get_current_object()
    if not request.json or "ids" not in request.json:
        abort(400)
    for package_id in request.json["ids"]:
        package = Package.query.get_or_404(package_id)
        # user can't buy the same package twice
        try:
            sponsorship = Sponsorship(event=event, sponsor=user, package=package)
        except exc.IntegrityError as err:  # need to test this
            return jsonify({"message": err, "url": url_for("main.event", id=event.id)})
        db.session.add(sponsorship)
    db.session.commit()
    return jsonify({"url": url_for("main.purchase", id=event.id)})


@main.route("/events/<int:id>/charge/<int:amount>", methods=["POST"])
@login_required
@permission_required(Permission.SPONSOR_EVENT)
def charge(id, amount):
    """View function to handle the POST request sent when a
    user makes a payment.
    """
    event = Event.query.get_or_404(id)
    user = current_user._get_current_object()
    # sponsorship deals for this event that haven't been completed yet
    sponsorships = Sponsorship.query.filter(
        Sponsorship.confirmation_code.is_(None),
        Sponsorship.sponsor_id == user.id,
        Sponsorship.event_id == event.id,
    ).all()
    if sponsorships == []:  # user has no pending deals for this event
        return redirect(url_for("main.index"))
    try:
        customer = current_app.stripe.Customer.create(
            email=request.form["stripeEmail"], source=request.form["stripeToken"]
        )
        charge = current_app.stripe.Charge.create(
            customer=customer.id,
            amount=amount,
            currency="usd",
            description="Sponsorship Deal",
        )
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
                flash("The package you attempted to purchase is sold out.")
                return redirect(url_for("main.event", id=event.id))
        db.session.commit()
        send_email(
            user.email,
            "Your Recent Purchase",
            "main/email/purchase",
            user=user,
            sponsorships=sponsorships,
            amount=amount,
        )
        flash("Your purchase was successful. A confirmation email was sent to you.")
        return redirect(url_for("main.manage_sponsorships", status="all"))
    # refactor needed. Maybe I can make a decorator to handle stripe errors?
    except current_app.stripe.error.CardError as err:
        # Since it's a decline, stripe.error.CardError will be caught
        db.session.rollback()
        flash("There was an error with your card, please try again.")
        return redirect(url_for("main.event", id=event.id))
    except current_app.stripe.error.RateLimitError as err:
        # Too many requests made to the API too quickly
        db.session.rollback()
        flash(
            "Sorry, we are experiencing high traffic volumes. Please wait 30 seconds before retrying your purchase."
        )
        return redirect(url_for("main.event", id=event.id))
    except current_app.stripe.error.InvalidRequestError as err:
        # Invalid parameters were supplied to Stripe's API
        db.session.rollback()
        flash("Invalid parameters were supplied, please try again.")
        return redirect(url_for("main.event", id=event.id))
    except current_app.stripe.error.AuthenticationError as err:
        # Authentication with Stripe's API failed
        db.session.rollback()
        flash(
            "We are having issues connecting to the Stripe API. We will try to resolve this issue as soon as possible. Please try to make your purchase again later."
        )
        return redirect(url_for("main.event", id=event.id))
    except current_app.stripe.error.APIConnectionError as err:
        # Network communication with Stripe failed
        db.session.rollback()
        flash(
            "We are having issues connecting to the Stripe API. We will try to resolve this issue as soon as possible. Please try to make your purchase again later."
        )
        return redirect(url_for("main.event", id=event.id))
    except current_app.stripe.error.StripeError as err:
        # Generic Stripe error
        db.session.rollback()
        flash(
            "We are having issues accessing the Stripe API. We will try to resolve this issue as soon as possible. Please try to make your purchase again later."
        )
        return redirect(url_for("main.event", id=event.id))
    except Exception as err:
        # Something else happened, completely unrelated to Stripe
        db.session.rollback()
        abort(500)


# need to lock the table to avoid a race condition
# then I need to decrement the quantity of available packages by 1 for
# each package that was purchased
@main.route("/events/<int:id>/sponsorships/purchase", methods=["GET", "POST"])
@login_required
@permission_required(Permission.SPONSOR_EVENT)
def purchase(id):
    """Return a page that allows the sponsor to complete their
    purchases of the package(s).
    """
    form = ContactForm()
    event = Event.query.get_or_404(id)
    user = current_user._get_current_object()
    endpoint = "main.purchase"
    publishable_key = current_app.config["STRIPE_PUBLISHABLE_KEY"]
    description = "Purchase Sponsorships"
    if form.validate_on_submit():
        send_email(
            organizer.email,
            f"Event Inquiry - {form.subject.data}",
            "main/email/contact_organizer",
            organizer=organizer,
            form=form,
            event=event,
        )
        flash("Your email was sent to the event organizer.")
        return redirect(url_for("main.purchase", id=event.id))
    # sponsorship deals for this event that haven't been completed yet
    amount = 0
    sponsorships = []
    for sponsorship in user.sponsorships:
        if sponsorship.event_id == event.id and sponsorship.is_pending():
            sponsorships.append(sponsorship)
            amount += sponsorship.package.price * 100
    url = url_for("main.charge", id=event.id, amount=amount)
    if sponsorships == []:  # user has no pending deals for this event
        return redirect(url_for("main.index"))
    flash(
        "Please note: Navigating away from or refreshing this page will cancel your purchase."
    )
    return render_template(
        "main/events/purchase.html",
        form=form,
        event=event,
        sponsorships=sponsorships,
        endpoint=endpoint,
        publishable_key=publishable_key,
        amount=amount,
        url=url,
    )


@main.route("/events/<int:id>/sponsorships/cancel_purchase", methods=["POST"])
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
        return redirect(url_for("main.manage_sponsorships", status="all"))
    else:  # someone attempts to visit this route outside of the payment process
        return redirect(url_for("main.manage_sponsorships", status="all"))


@main.route("/admin_panel/<role_name>")
@login_required
@admin_required
def admin_panel(role_name):
    """Return a page that allows a user with administrator priveleges
    to manage the website."""
    roles = [(1, "All"), (2, "Sponsor"), (3, "Event Organizer"), (4, "Administrator")]
    dropdown_form = DropdownForm(roles)
    if role_name == "all":
        users = User.query.all()
    else:
        role = Role.query.filter_by(name=role_name.title()).first_or_404()
        users = User.query.filter_by(role=role).all()
    reverse_roles = {role_name.lower(): number for number, role_name in roles}
    dropdown_form.options.data = reverse_roles[role_name]
    return render_template(
        "main/users/admin_panel.html", users=users, dropdown_form=dropdown_form
    )
