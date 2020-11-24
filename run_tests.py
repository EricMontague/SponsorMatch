"""This file contains a cli command to execute tests for the application."""


import os
import sys
import click
import unittest


# add the root project directory to the python path so that the app directory
# and all subdirectories are able to be imported during tests
directory = os.path.dirname(__file__)
if directory not in sys.path:
    sys.path.insert(0, directory)




@click.command()
@click.option(
    "--coverage/--no-coverage", default=False, help="Run tests under code coverage."
)
@click.argument("test_names", nargs=-1)
def run_tests(coverage, test_names):
    """Run the unit tests. Typing the --no-coverage option or leaving
    the OPTION field blank, will run the unit tests without printing a
    coverage report. Must be run from the root directory of the project.
    """
    COV = None
    if coverage or os.environ.get("FLASK_COVERAGE", False):
        import coverage

        COV = coverage.coverage(branch=True, include="app/*")
        COV.start()

    if test_names:
        print("Loading tests from names...\n")
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        print("Running unittest test discvoery...\n")
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


if __name__ == "__main__":
    run_tests()