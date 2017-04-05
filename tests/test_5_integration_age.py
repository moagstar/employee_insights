# 3rd party
from hypothesis import given
# local
from employee_insights.queries import get_employees_percentage_older_than_average as get_expected
from tests.fixtures import page
from tests.common import perform_integration_test
from tests.strategies import employee_database_sessions


@given(employee_database=employee_database_sessions())
def test_integration_age(session, page):
    """
    Verify that getting the percentage of employees older than the company average works end to
    end (load page -> set params -> query -> result).

    :param page: The capybara page with the age view loaded.
    :param employee_database: tuple of (employee data, SQLAlchemy session)
                              which should be used for testing.
    """
    tests = ({'n_years': n} for n in range(0, 10))

    results_columns = [
        lambda x: x['company_name'],
        lambda x: int(float(x['average_employee_age'])),
        lambda x: int(float(x['percentage_older'])),
    ]
    perform_integration_test(session, page, 'age', tests, get_expected, results_columns)
