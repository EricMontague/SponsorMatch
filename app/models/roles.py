"""This module contains models related to roles and user permissions."""


from app.extensions import db


class Permission:
    """Class to represent user permissions."""

    CREATE_EVENT = 1
    SPONSOR_EVENT = 2
    ADMIN = 4


class Role(db.Model):
    """Class to represent the different user roles"""

    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    permissions = db.Column(db.Integer, default=0, nullable=False)
    users = db.relationship("User", backref="role", lazy="dynamic")

    @staticmethod
    def insert_roles():
        """Insert role names into the roles table"""
        role_names = {
            "Event Organizer": [Permission.CREATE_EVENT],
            "Sponsor": [Permission.SPONSOR_EVENT],
            "Administrator": [
                Permission.CREATE_EVENT,
                Permission.SPONSOR_EVENT,
                Permission.ADMIN,
            ],
        }
        for role_name in role_names:
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name)
            role.reset_permissions()
            for perm in role_names[role_name]:
                role.add_permissions(perm)
            db.session.add(role)
        db.session.commit()

    def add_permissions(self, perm):
        """Grant a user the given permissions."""
        if not self.has_permissions(perm):
            self.permissions += perm

    def remove_permissions(self, perm):
        """Remove the given permissions."""
        if self.has_permissions(perm):
            self.permissions -= perm

    def reset_permissions(self):
        """Reset all user permissions"""
        self.permissions = 0

    # need to review this
    def has_permissions(self, perm):
        """Return True if the user has the given permissions."""
        return self.permissions & perm == perm

    def __repr__(self):
        """Return a string representation of the role class. Used
        for debugging purposes
        """
        return "<Role: %r>" % self.name
