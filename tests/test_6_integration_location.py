# std
from itertools import product
# 3rd party
from hypothesis import given
# local
from employee_insights import database
from employee_insights.queries import get_employees_percentage_by_location as get_expected, get_locations
from tests.fixtures import page
from tests.common import perform_integration_test
from tests.strategies import employee_database_sessions


@given(employee_database=employee_database_sessions())
def test_integration_location(session, page):
    """
    Verify that getting the percentage of employees at a particular location works end to
    end (load page -> set params -> query -> result).

    :param page: The capybara page with the location view loaded.
    :param employee_database: tuple of (employee data, SQLAlchemy session)
                              which should be used for testing.
    """
    min_percentages = ({'min_percentage': n} for n in range(0, 10))
    tests = product(get_locations(database.session), min_percentages)

    results_columns = [
        lambda x: x['company_name'],
        lambda x: x['location'],
        lambda x: int(float(x['percentage'])),
    ]
    perform_integration_test(session, page, 'location', tests, get_expected, results_columns)
