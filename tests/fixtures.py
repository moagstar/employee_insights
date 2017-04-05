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


capybara.default_max_wait_time = 5


@pytest.fixture
def page():
    """
    Create a capybara page for use in an integration test.

    :return: The capybara page.
    """
    if capybara.app != app:
        capybara.app = app
    return capybara.dsl.page