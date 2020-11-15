"""This module contains the view functions for the auth blueprint."""


from flask import (
    render_template,
    url_for,
    flash,
    redirect,
    request,
    abort,
    g,
    session,
    current_app,
)
from flask_login import login_user, logout_user, login_required, current_user
from app.common import send_email
from app.blueprints.auth import auth
from app.blueprints.auth.forms import (
    LoginForm,
    RegistrationForm,
    PasswordResetRequestForm,
    PasswordResetForm,
)
from app.blueprints.main.forms import SearchForm
from app.models import User, Role
from app.extensions import db, login_manager
from app.blueprints.auth import services


def redirect_to_next_url(fallback_endpoint):
    """Redirect the user to the url they were trying to navigate
    to. If there is no next url, redirect to the fallback endpoint.
    """
    next_url = request.args.get("next")
    if next_url is None or not next_url.startswith("/"):
        next_url = url_for(fallback_endpoint)
    return redirect(next_url)


@auth.before_app_request
def before_request():
    """Application level request hook that adds the search form
    to Flask's g context variable so that it can be accessed in
    all templates.
    """
    g.search_form = SearchForm()


@login_manager.user_loader
def load_user(user_id):
    """Given a user_id, return the associated user object"""
    return User.query.get(int(user_id))


@auth.route("/login", methods=["GET", "POST"])
def login():
    """View function to handle user logins"""
    form = LoginForm()
    if form.validate_on_submit():
        form_data = {
            "email": form.email.data,
            "password": form.password.data,
            "remember_me": form.remember_me.data,
        }
        try:
            user = services.login_user(form_data, User.query, login_user)
        except services.InvalidLoginCredentials as err:
            flash(str(err), "danger")
        else:
            return redirect_to_next_url("main.index")
    return render_template("auth/login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    """View function to handle user logouts"""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    """View function to handle user registration"""
    form = RegistrationForm()
    if form.validate_on_submit():
        user = services.register_user(
            form.data, current_app.config["ADMIN_EMAIL"], db.session
        )
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth.route("/request-password-reset", methods=["GET", "POST"])
def request_password_reset():
    """View function for when a user forgets their password
    and makes a request to reset it
    """
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        try:
            services.initiate_password_reset(form.email.data)
        except services.InvalidEmail as err:
            flash(str(err), "danger")
        else:
            flash(
                "An email with instructions to reset your password has been "
                "sent to your email address.",
                "info",
            )
            session["password_reset_initiated"] = True
            return redirect(url_for("auth.login"))
    return render_template("auth/forgot_password.html", form=form)


@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """View function for when a user resets their password"""
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = PasswordResetForm()
    if session.get("password_reset_initiated"):
        if form.validate_on_submit():
            if User.reset_password(token, form.password.data):
                db.session.commit()
                flash("Your password was successfully changed.", "success")
                session["password_reset_initiated"] = False
                return redirect(url_for("auth.login"))
            else:
                flash("Your password reset was unsuccessful.", "danger")
                return redirect(url_for("main.index"))
        return render_template("auth/reset_password.html", form=form)
    return redirect(url_for("main.index"))
