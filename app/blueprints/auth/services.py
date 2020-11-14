"""This module contains functions that serve to abstract away
authentication operations.
"""

from app.models import User, Role
from app.common import send_email


class InvalidLoginCredentials(Exception):
    pass


class InvalidEmail(Exception):
    pass


def login_user(form_data, query, store_user_session):
    """Validate that the user supplied the correct email and
    password in the login form. Return the logged in user if
    successful, else throw and InvalidLognCredentials exception.
    """
    user = query.filter_by(email=form_data["email"]).first()
    if user is not None and user.verify_password(form_data["password"]):
        store_user_session(user, form_data["remember_me"])
        return user
    else:
        raise InvalidLoginCredentials("Invalid email or password")


def register_user(form_data, admin_email, db_session):
    """Return a new registered user from the registration form data."""
    if form_data["email"] == admin_email:
        role = Role.query.filter_by(name="Administrator").first()
    else:
        role = Role.query.get(form_data["role"])
    # replace role field with role object
    form_data["role"] = role
    user = User.create(**form_data)
    db_session.commit()
    return user


def initiate_password_reset(email):
    """Send the user an email to start the password reset process."""
    user = User.query.filter_by(email=email).first()
    if user is not None:
        token = user.generate_password_reset_token()
        send_email(
            user.email,
            "Reset Your Password",
            "auth/email/reset_password",
            user=user,
            token=token,
        )
    else:
        raise InvalidEmail("We couldn't find an account with that email address")

