# std
import datetime
import itertools
# 3rd party
from hypothesis import given, settings
# local
from employee_insights.queries import get_employees_per_company
from tests.strategies import employee_databases
from tests.common import get_company_employees


today = datetime.date(2017, 4, 1)


def get_expected(employee_data):
    """
    Get the number of all employees per company using python.

    :param employee_data: Hypothesis generated employee database source data.

    :return: Generator which when iterated yields a tuple of company_id, count
             which represents the expected result from get_employees_per_company.
    """
    for company, company_employees in get_company_employees(employee_data):
        yield company.company_id, len(company_employees)


@settings(max_examples=50)
@given(employee_databases())
def test_get_employees_per_company(employee_database):
    """
    Verify that the query in get_employees_per_company behaves as expected.
    The way this is verified is by performing the same calculation in python
    rather than sql. The idea being that if two different calculation methods
    produce the same output we can be more confident that both are correct.

    :param employee_database: tuple of (employee data, SQLAlchemy session)
                              which should be used for testing.
    """
    employee_data, session = employee_database

    actual_result = sorted(get_employees_per_company(session))
    expected_result = sorted(get_expected(employee_data))

    for actual, expected in itertools.zip_longest(actual_result, expected_result):
        company_id, total = expected
        assert actual.company_id == company_id
        assert actual.total == total
