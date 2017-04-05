# std
import datetime
import collections
import itertools
# 3rd party
import pytest
from hypothesis import given, settings
# local
from employee_insights.queries import get_employees_percentage_per_job_title
from strategies import employee_databases
from common import get_company_employees

today = datetime.date(2017, 4, 1)


def get_expected(employee_data):
    """
    Calculate the percentage of employees of a company that have a particular
    job title using python.

    :param employee_data: Hypothesis generated employee database source data.

    :return: Generator which when iterated yields a tuple of
             (company_id, count, percentage)
             which represents the expected result from
             get_employees_percentage_per_job_title.
    """
    for company, company_employees in get_company_employees(employee_data):
        counter = collections.Counter(x.job_title_id for x in company_employees)
        for job_title_id, count in counter.items():
            percentage = float(count) / len(company_employees) * 100
            yield company.company_id, job_title_id, percentage


@settings(max_examples=50)
@given(employee_databases())
def test_get_employees_percentage_per_job_title(employee_database):
    """
    Verify that the query in get_employees_percentage_per_job_title behaves as
    expected. The way this is verified is by performing the same calculation
    in python rather than sql. The idea being that if two different calculation
    methods produce the same output we can be more confident that both are
    correct.

    :param employee_database: tuple of (employee data, SQLAlchemy session)
                              which should be used for testing.
    """
    employee_data, session = employee_database

    actual_result = sorted(get_employees_percentage_per_job_title(session))
    expected_result = sorted(get_expected(employee_data))

    for actual, expected in itertools.zip_longest(actual_result, expected_result):

        company_id, job_title_id, percentage = expected

        assert actual.company_id == company_id
        assert actual.job_title_id == job_title_id
        assert pytest.approx(float(actual.percentage), 0.1) == percentage

        # besides checking against the python implementation we can also
        # perform these sanity checks.
        for company in actual_result:
            assert 0 <= company.percentage <= 100
