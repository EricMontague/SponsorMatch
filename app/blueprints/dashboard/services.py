"""This module contains functions that serve as abstractions
for operations in the dashboard blueprint.
"""

from app.models import User, Role


def get_users_by_role(role_name):
    """Return a list of users based on the role provided."""
    if role_name == "all":
        users = User.query.all()
    else:
        users = User.query.join(Role, Role.id == User.role_id).filter(Role.name == role_name).all()
    return users