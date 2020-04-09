"""This script runs the application and contains some
convenient command line tools
"""


import os
import click
import sys
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


app = create_app(os.environ.get("FLASK_CONFIG") or "default")
migrate.init_app(app, db)



COV = None
if os.environ.get("FLASK_COVERAGE"):
    import coverage

    COV = coverage.coverage(branch=True, include="app/*")
    COV.start()


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
    )


#temporary cli command to setup the environment. will delete this later
#in favor of Docker containers
@app.cli.command()
@click.option(
    "--fake-data/--no-fake-data", default=True, help="Setup the developement environment."
)
def setup_environment(fake_data):
    """Cli command to setup the development environment. Starts up
    Elasticsearch, sets up the database and inserts fake data into
    the database if request.
    """
    #create database tables if they don't already exist
    db.create_all()

    # create or update roles, event types, categories, and image types
    Role.insert_roles()
    EventType.insert_event_types()
    EventCategory.insert_event_categories()
    ImageType.insert_image_types()

    #add fake data to the database
    if fake_data:
        fake = FakeDataGenerator(40, 40)
        fake.add_all()



@app.cli.command()
@click.option(
    "--coverage/--no coverage", default=False, help="Run tests under code coverage."
)
@click.argument("test_names", nargs=-1)
def test(coverage, test_names):
    """Run the unit tests. Typing the --no-coverage option or leaving
    the OPTION field blank, will run the unit tests without printing a
    coverage report.
    """
    if coverage and not os.environ.get("FLASK_COVERAGE"):
        import subprocess

        os.environ["FLASK_COVERAGE"] = "1"
        sys.exit(subprocess.call(sys.argv))

    import unittest

    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover("tests", pattern="test*.py")
    unittest.TextTestRunner(verbosity=2).run(tests)
    # executes only if the --coverage option was typed
    if COV:
        COV.stop()
        COV.save()
        print("Coverage Summary: ")
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, "tmp/coverage")
        COV.html_report(directory=covdir)
        print(f"HTML version file://{covdir}/index.html")
        COV.erase()


@app.cli.command()
@click.option(
    "--fake-data/--no-fake-data", default=False, help="Add fake data to the database before deployment."
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

    #add fake data to the database
    if fake_data:
        fake = FakeDataGenerator(40, 40)
        fake.add_all()


if __name__ == "__main__":
    app.run(debug=True)
