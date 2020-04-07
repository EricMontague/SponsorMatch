"""This module contains functions to be used as decorators throughout
the application.
"""
import functools
from flask import abort
from flask_login import current_user
from app.models.roles import Permission


def permission_required(permission):
    """Function to be used as a decorator to check
	user permissions.
	"""
    def decorator(func):
        @functools.wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return func(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(func):
    """Check if the user has admim permissions."""
    return permission_required(Permission.ADMIN)(func)
