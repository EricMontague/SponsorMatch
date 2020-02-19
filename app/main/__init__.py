from flask import Blueprint


main = Blueprint("main", __name__)

from . import views, errors
from ..models import Permission, EventStatus, SponsorshipStatus


# makes the Permission class available to all templates
@main.app_context_processor
def inject_permissions():
    return dict(
        Permission=Permission,
        EventStatus=EventStatus,
        SponsorshipStatus=SponsorshipStatus,
    )
