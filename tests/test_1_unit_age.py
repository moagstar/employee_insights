# std
from unittest import mock
import datetime
import statistics
import itertools
import collections
from toolz.itertoolz import count
# 3rd party
import pytest
from hypothesis import strategies as st, given, settings
# local
from employee_insights.queries import get_employees_percentage_older_than_average
from tests.strategies import employee_databases
from tests.common import get_company_employees


today = datetime.date(2017, 4, 1)


Expected = collections.namedtuple('Expected', [
    'company_id',
    'company_name',
    'average_employee_age',
    'percentage_older',
])


def get_expected(employee_data, years):
    """
    Get the expected percentage of all employees per company that are
    specified number of years older than the company-wide average using
    python.

    :param employee_data: Hypothesis generated employee database source data.
    :param years: Find percentage of employees this number of years older
                    than the company-wide average.

    :return: Generator which when iterated yields an instance of ``Expected``
             which represents the expected result from get_employees_per_company.
    """
    for company, company_employees in get_company_employees(employee_data):

        percentage_older = 0

        def calc_age(employee):
            return (today - employee.date_of_birth).days / 365.25

        employee_ages = list(map(calc_age, company_employees))
        average_employee_age = statistics.mean(employee_ages)

        def is_older(employee_age):
            return employee_age > (average_employee_age + years)

        n_employees_older = count(filter(is_older, employee_ages))

        if n_employees_older:
            n_employees = float(len(company_employees))
            percentage_older = n_employees_older / n_employees * 100

        yield Expected(company.company_id, company.company_name,
                       average_employee_age, percentage_older)


@settings(max_examples=50)
@given(employee_databases(), st.integers(min_value=0, max_value=10))
def test_get_employees_percentage_older_than_average(employee_database, years):
    """
    Verify that the query in get_employees_percentage_older_than_average
    behaves as expected. The way this is verified is by performing the same
    calculation in python rather than sql. The idea being that if two different
    calculation methods produce the same output we can be more confident that
    both are correct.

    :param employee_database: tuple of (employee data, SQLAlchemy session)
                              which should be used for testing.
    :param years: Find percentage of employees this number of years older
                    than the company-wide average.
    """
    with mock.patch('employee_insights.models.NOW', '2017-04-01'):

        employee_data, session = employee_database

        actual_result = sorted(get_employees_percentage_older_than_average(session, years))
        expected_result = sorted(get_expected(employee_data, years))

        for actual, expected, in itertools.zip_longest(actual_result, expected_result):
            company_id, company_name, average_employee_age, percentage_older = expected
            assert actual.company_id == company_id
            assert pytest.approx(float(actual.percentage_older), 0.1) == percentage_older

        # besides checking against a python implementation there are also a
        # number of other sanity checks we can perform
        for company in actual_result:
            assert 0 <= company.percentage_older <= 100
            expected_company = employee_data.companies[company.company_id-1]
            assert company.company_name == expected_company.company_name
