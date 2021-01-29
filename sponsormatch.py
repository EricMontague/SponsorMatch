"""This script runs the application and contains some
convenient command line tools
"""


import os
import click
import sys
from dotenv import load_dotenv


load_dotenv()


from app import create_app
from app.fake import FakeDataGenerator
from app.models import (
    User,
    Role,
    Image,
    Event,
    EventType,
    Venue,
    EventCategory,
    ImageType,
    Package,
    Video,
    Permission,
    Sponsorship,
)
from flask_migrate import upgrade
from app.extensions import db, migrate
from app.error_handlers import (
    page_not_found,
    internal_server_error,
    bad_request,
    forbidden,
)
from werkzeug.exceptions import (
    NotFound,
    InternalServerError,
    BadRequest,
    Forbidden,
)
from app.search import MatchQuery, BooleanQuery, ElasticsearchClient


app = create_app(
    os.environ.get("FLASK_CONFIG", "default"),
    os.environ.get("USE_ELASTICSEARCH", 1) == 1,
)

# Register application wide error handlers
app.register_error_handler(NotFound, page_not_found)
app.register_error_handler(InternalServerError, internal_server_error)
app.register_error_handler(BadRequest, bad_request)
app.register_error_handler(Forbidden, forbidden)

# Register with Flask-Migrate
migrate.init_app(app, db)


@app.shell_context_processor
def make_shell_context():
    """Allow the models to be automatically imported
    when a flask shell session is started
    """
    return dict(
        db=db,
        User=User,
        Role=Role,
        Image=Image,
        Event=Event,
        EventType=EventType,
        Venue=Venue,
        EventCategory=EventCategory,
        ImageType=ImageType,
        Package=Package,
        Video=Video,
        Permission=Permission,
        Sponsorship=Sponsorship,
        MatchQuery=MatchQuery,
        BooleanQuery=BooleanQuery,
    )


@app.context_processor
def uilitity_functions():
    """Allow utility functions to be available
    for use throught templates.
    """

    def print_in_template(message):
        print(str(message))

    return dict(debug=print_in_template)



@app.cli.command()
@click.option(
    "--fake-data/--no-fake-data",
    default=False,
    help="Setup the developement environment.",
)
def setup_environment(fake_data):
    """Cli command to setup the development environment. Starts up
    Elasticsearch, sets up the database and inserts fake data into
    the database if request.
    """
    app.sqlalchemy_search_middleware._elasticsearch_client.delete_index(Event.__tablename__)
    db.drop_all()
    db.create_all()

    # create or update roles, event types, categories, and image types
    Role.insert_roles()
    EventType.insert_event_types()
    EventCategory.insert_event_categories()
    ImageType.insert_image_types()

    # add fake data to the database
    if fake_data:
        fake = FakeDataGenerator(48, 48)
        fake.add_all()




@app.cli.command()
@click.option(
    "--fake-data/--no-fake-data",
    default=False,
    help="Add fake data to the database before deployment.",
)
def deploy(fake_data):
    """Run the below set of tasks before deployment."""
    # migrate database to latest revision
    upgrade()

    # create or update roles, event types, categories, and image types
    Role.insert_roles()
    EventType.insert_event_types()
    EventCategory.insert_event_categories()
    ImageType.insert_image_types()

    es_client = ElasticsearchClient(app.config["ELASTICSEARCH_URL"])
    es_client.create_index("events")
    # add fake data to the database if there isn't already fake data in the tables
    if fake_data:
        fake = FakeDataGenerator(48, 48)
        fake.add_all()        


if __name__ == "__main__":
    app.run(debug=True)
