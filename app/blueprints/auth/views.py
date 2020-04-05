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
from app.helpers import send_email
from auth import auth
from auth.forms import (
    LoginForm,
    RegistrationForm,
    PasswordResetRequestForm,
    PasswordResetForm,
)
from app.main.forms import SearchForm
from app.models import User, Role
from app.extensions import db, login_manager


@auth.route("/login", methods=["GET", "POST"])
def login():
    """View function to handle user logins"""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next_url = request.args.get("next")
            if next_url is None or not next_url.startswith("/"):
                next_url = url_for("main.index")
            return redirect(next_url)
        flash("Invalid email or password.")
    return render_template("auth/login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    """View function to handle user logouts"""
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("main.index"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    """View function to handle user registration"""
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        if email == current_app.config["ADMIN_EMAIL"]:
            role = Role.query.filter_by(name="Administrator").first()
        else:
            role = Role.query.get(form.role.data)
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            company=form.company.data,
            email=email,
            password=form.password.data,
            role=role,
        )
        db.session.add(user)
        db.session.commit()
        if user.role.name == "Event Organizer":
            flash(
                "Registration successful!. You will be asked for your payment information upon login."
            )
        else:
            flash("Registration successful!. Please login.")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth.route("/payments")
@login_required
def payments():
    """Return the template for the page that allows the user to enter 
    their payment information.
    """
    if (
        current_user.is_anonymous
        or current_user.has_paid
        or current_user.role.name != "Event Organizer"
    ):
        return redirect(url_for("main.index"))
    publishable_key = current_app.config["STRIPE_PUBLISHABLE_KEY"]
    description = "Purchase Subscription"
    amount = 2999
    url = url_for("auth.charge", amount=amount)
    return render_template(
        "auth/payments.html",
        publishable_key=publishable_key,
        description=description,
        url=url,
        amount=amount,
    )


@auth.route("/charge/<int:amount>", methods=["POST"])
@login_required
def charge(amount):
    """View function to handle the POST request sent when a
    user makes a payment.
    """
    # need to add more validation to this route
    if (
        current_user.is_anonymous
        or current_user.has_paid
        or current_user.role.name != "Event Organizer"
    ):
        return redirect(url_for("main.index"))
    try:
        customer = current_app.stripe.Customer.create(
            email=request.form["stripeEmail"], source=request.form["stripeToken"]
        )
        charge = current_app.stripe.Charge.create(
            customer=customer.id,
            amount=amount,
            currency="usd",
            description="Purchase Subscription",
        )
        current_user.has_paid = True
        db.session.commit()
        send_email(
            customer.email,
            "Welcome!",
            "auth/email/confirmation",
            user=current_user,
            charge=charge,
        )
        flash("A confirmation email has been sent to your email address.")
        return redirect(url_for("main.index"))
    except current_app.stripe.error.StripeError:
        abort(500)


@auth.before_app_request
def before_request():
    """Application level request hook that redirects as user to
    the payments view if they try to access a page without first
    paying for their subscription.
    """
    g.search_form = SearchForm()
    if current_user.is_authenticated:
        if (
            not current_user.has_paid
            and current_user.role.name == "Event Organizer"
            and request.endpoint
            and request.blueprint != "auth"
            and request.endpoint != "static"
        ):
            return redirect(url_for("auth.payments"))


@login_manager.user_loader
def load_user(user_id):
    """Given a user_id, return the associated user object"""
    return User.query.get(int(user_id))


@auth.route("/request_password_reset", methods=["GET", "POST"])
def request_password_reset():
    """View function for when a user forgets their password
    and makes a request to reset it
    """
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None:
            token = user.generate_password_reset_token()
            send_email(
                user.email,
                "Reset Your Password",
                "auth/email/reset_password",
                user=user,
                token=token,
            )
            flash(
                "An email with instructions to reset your password has been "
                "sent to your email address."
            )
            session["password_reset"] = True
            return redirect(url_for("auth.login"))
        else:
            flash("We couldn't find an account with that email address")
    return render_template("auth/forgot_password.html", form=form)


@auth.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """View function for when a user resets their password"""
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = PasswordResetForm()
    if session.get("password_reset"):
        if form.validate_on_submit():
            if User.reset_password(token, form.password.data):
                db.session.commit()
                flash("Your password was successfully changed.")
                session["password_reset"] = False
                return redirect(url_for("auth.login"))
            else:
                flash("Your password reset was unsuccessful.")
                return redirect(url_for("main.index"))
        return render_template("auth/reset_password.html", form=form)
    return redirect(url_for("main.index"))
