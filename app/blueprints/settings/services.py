"""This module contains functions to abstract away some operations in
the settings blueprint.
"""

from app.utils import send_email


class InvalidPassword(Exception):
    pass


def change_email_request(user, new_email):
    token = user.generate_change_email_token(new_email)
    send_email(
        new_email,
        "Change Email Address",
        "settings/email/confirm_email_change",
        user=user,
        token=token,
    )
