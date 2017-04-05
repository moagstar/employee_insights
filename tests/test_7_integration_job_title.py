# 3rd party
from hypothesis import given
# local
from employee_insights.queries import get_employees_percentage_older_than_average as get_expected
from tests.fixtures import page
from tests.common import perform_integration_test
from tests.strategies import employee_database_sessions


@given(employee_database=employee_database_sessions())
def test_integration_job_title(session, page):
    """
    Verify that getting the percentage of employees with a particular job title works end to
    end (load page -> query -> result).

    :param page: The capybara page with the job_title view loaded.
    :param employee_database: tuple of (employee data, SQLAlchemy session)
                              which should be used for testing.
    """
    results_columns = [
        lambda x: x['company_name'],
        lambda x: x['job_title'],
        lambda x: round(float(x['percentage']), 2),
    ]
    perform_integration_test(session, page, 'location', [], get_expected, results_columns)
