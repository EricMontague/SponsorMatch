"""This module contains models related to sponsorship packages."""


from app.extensions import db


class Package(db.Model):
    """Class to represent a sponsorship package."""

    __tablename__ = "packages"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    price = db.Column(db.Numeric(6, 2), nullable=False)
    audience = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=True)
    num_purchased = db.Column(db.Integer, default=0, nullable=False)
    available_packages = db.Column(db.Integer, nullable=False) #num packages made avaiable originally
    package_type = db.Column(db.String(64), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    sponsorships = db.relationship("Sponsorship", back_populates="package")

    def is_sold_out(self):
        """Return True if the package is sold out."""
        return self.num_purchased == self.available_packages

    def num_for_sale(self):
        """Return the number of available packages."""
        return self.available_packages - self.num_purchased

    def __repr__(self):
        """Return the string representation of a Package.
        Used for debugging purposes.
        """
        return "<Package Name: %r>" % self.name
