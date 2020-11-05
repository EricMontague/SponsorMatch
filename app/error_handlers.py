"""This module contains functions which handle errors that
occur in the application.
"""


from flask import render_template
from http import HTTPStatus


def page_not_found(error):
    """Render a 404 error page to the user and return
    the error status code.
    """
    title = "Page Not Found"
    message = (
        "Oops! looks like the page you're looking for doesn't exist. "
        + "Please navigate back to the homepage and try again."
    )
    return (
        render_template("errors/error.html", title=title, message=message),
        HTTPStatus.NOT_FOUND,
    )


def internal_server_error(error):
    """Render a 500 error page to the user and return
    the error status code.
    """
    title = "Internal Server Error"
    message = (
        "It looks as if we're having some technical difficulties at the moment. "
        + "Please retry your action again in a few seconds."
    )
    return (
        render_template("errors/error.html", title=title, message=message),
        HTTPStatus.INTERNAL_SERVER_ERROR,
    )


def forbidden(error):
    """Render a 403 error page to the user and return
    the error status code.
    """
    title = "Forbidden"
    message = (
        "Oops! looks like you don't have access to this url. "
        + "Please navigate back to the homepage and try again."
    )
    return render_template("errors/error.html", title=title, message=message), HTTPStatus.FORBIDDEN


def bad_request(error):
    """Renders a 400 error page to the user and return
    the error status code.
    """
    title = "Bad Request"
    message = (
        "Oops! looks like the request you made includes invalid data. "
        + "Please double check your information and try again."
    )
    return render_template("errors/error.html", title=title, message=message), HTTPStatus.BAD_REQUEST
