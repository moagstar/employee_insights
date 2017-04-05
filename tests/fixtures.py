# std
import os
# 3rd party
import pytest
import capybara
import capybara.dsl
# local
from employee_insights.app import app
from employee_insights import database
from strategies import employee_databases


@pytest.yield_fixture
def page():

    employee_data, database.session = employee_databases().example()

    app.config['BOOTSTRAP_SERVE_LOCAL'] = True
    capybara.app = app
    __dir__ = os.path.dirname(__file__)
    bin_path = os.path.join(__dir__, 'bin')
    os.environ["PATH"] = os.pathsep.join((bin_path, os.environ["PATH"]))

    try:
        yield capybara.dsl.page
    finally:
        pass