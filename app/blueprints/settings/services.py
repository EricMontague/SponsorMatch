"""This module contains functions to abstract away some operations in
the settings blueprint.
"""

from app.helpers import send_email


class InvalidPassword(Exception):
    pass


def change_email_request(user, new_email, password):
    if user.verify_password(password):
        token = user.generate_change_email_token(new_email)
        send_email(
            new_email,
            "Change Email Address",
            "settings/email/confirm_email_change",
            user=user,
            token=token,
        )
    else:
        raise InvalidPassword("You entered an invalid password.")