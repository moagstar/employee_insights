# std
import os
# 3rd party
import pytest
import capybara
import capybara.dsl
# local
from employee_insights.app import app
from employee_insights import database


# setup capybara / selenium
__dir__ = os.path.dirname(__file__)
bin_path = os.path.join(__dir__, 'bin')
os.environ["PATH"] = os.pathsep.join((bin_path, os.environ["PATH"]))
app.config['BOOTSTRAP_SERVE_LOCAL'] = True


@pytest.yield_fixture
def page():
    """
    Create a capybara page for use in an integration test. The current database session is saved
    on entry and restored on exit.

    :return: The capybara page.
    """
    old_session = database.session
    try:
        capybara.app = app
        yield capybara.dsl.page
    finally:
        database.session = old_session
        capybara.reset_sessions()
