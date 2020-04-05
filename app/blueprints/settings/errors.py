"""This module contains functions which handle errors that
occur in the settings blueprint.
"""


from flask import render_template
from main import main


@settings.app_errorhandler(404)
def page_not_found(error):
    """Render a 404 error page to the user and return
	the error status code.
	"""
    return render_template("error_codes/404.html"), 404


@settings.app_errorhandler(500)
def internal_server_error(error):
    """Render a 500 error page to the user and return
	the error status code.
	"""
    return render_template("error_codes/500.html"), 500


@settings.app_errorhandler(403)
def forbidden(error):
    """Render a 403 error page to the user and return
	the error status code.
	"""
    return render_template("error_codes/403.html"), 403


@settings.app_errorhandler(400)
def bad_request(error):
    """Renders a 400 error page to the user and return
	the error status code.
	"""
    return render_template("error_codes/400.html"), 400
