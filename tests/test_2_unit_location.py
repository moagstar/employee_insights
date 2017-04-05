# std
import datetime
import itertools
from functools import partial
# 3rd party
import pytest
from hypothesis import strategies as st, given, settings
from neobunch import NeoBunch as Bunch
from toolz.itertoolz import count
# local
from employee_insights.queries import get_employees_percentage_by_location
from tests.strategies import employee_databases
from tests.common import get_company_employees


today = datetime.date(2017, 4, 1)


def get_expected(employee_data, continent, country, state, city, min_percentage):
    """
    Calculate the percentage of employees of a company at a particular location,
    filtered by a minimum percentage of employees using python.

    :param employee_data: Hypothesis generated employee database source data.
    :param continent: Get percentage of employees in this continent.
    :param country: Get percentage of employees in this country.
    :param state: Get percentage of employees in this state.
    :param city: Get percentage of employees in this city.
    :param min_percentage: The minimum percentage of employees a location should
                           have to be included in the output.

    :return: Generator which when iterated yields a tuple of
             (company_id, location, percentage)
             which represents the expected result from
             get_employees_percentage_by_location.
    """
    params = Bunch(continent=continent, country=country, state=state, city=city)

    location_fields = ['city', 'state', 'country', 'continent']

    def get_location(employee):
        return employee_data.locations[employee.location_id - 1]

    def are_all_attrs_equal(lhs, rhs, attrs):
        return all(getattr(lhs, attr) == getattr(rhs, attr) for attr in attrs)

    def get_location_and_where(n):
        """
        Get the location to include in the result and a where function to
        filter the company employees for inclusion when calculating the
        percentage at a location.
        """
        fields = location_fields[n:]
        filter_func = partial(are_all_attrs_equal, params, attrs=fields)
        employee_location = next(filter(filter_func, employee_data.locations))

        location = '/'.join(
            getattr(employee_location, x)
            for x in reversed(fields)
        )

        def where(employee):
            return are_all_attrs_equal(get_location(employee), params, fields)

        return location, where

    for company, company_employees in get_company_employees(employee_data):

        if city:
            location, where = get_location_and_where(0)
        elif state:
            location, where = get_location_and_where(1)
        elif country:
            location, where = get_location_and_where(2)
        else:
            location, where = get_location_and_where(3)

        n_employees_in_location = count(filter(where, company_employees))
        n_employees = float(len(company_employees))
        percentage = n_employees_in_location / n_employees * 100

        if 0 < percentage > min_percentage:
            yield company.company_id, location, percentage


def get_test_location(draw, employee_data):

    country, state, city = [None] * 3

    continent = draw(st.sampled_from(employee_data.locations)).continent

    if draw(st.booleans()):
        country = draw(st.sampled_from(employee_data.locations)).country

        if draw(st.booleans()):
            state = draw(st.sampled_from(employee_data.locations)).state

            if draw(st.booleans()):
                city = draw(st.sampled_from(employee_data.locations)).city

    location = '/'.join(x for x in (continent, country, state, city) if x)
    return location, continent, country, state, city


@settings(max_examples=50)
@given(employee_databases(), st.data(), st.integers(min_value=0, max_value=100))
def test_get_employees_percentage_by_location(employee_database, data, min_percentage):
    """
    Verify that the query in get_employees_percentage_by_location behaves as
    expected. The way this is verified is by performing the same calculation
    in python rather than sql. The idea being that if two different calculation
    methods produce the same output we can be more confident that both are
    correct.

    :param employee_database: tuple of (employee data, SQLAlchemy session)
                              which should be used for testing.
    :param data: Hypothesis strategy for interactively drawing additional
                 examples.
    :param min_percentage: The minimum percentage a location should meet to be
                           included in the result set.
    """
    employee_data, session = employee_database

    location, continent, country, state, city = get_test_location(data.draw, employee_data)

    actual_result = get_employees_percentage_by_location(session, location, min_percentage)
    actual_result = sorted(actual_result)

    expected_result = get_expected(employee_data, continent, country, state, city, min_percentage)
    expected_result = sorted(expected_result)

    for actual, expected in itertools.zip_longest(actual_result, expected_result):

        company_id, location, percentage = expected

        assert actual.company_id == company_id
        assert actual.location == location
        assert pytest.approx(float(actual.percentage), 0.1) == percentage

        # besides checking against the python implementation we can also
        # perform these sanity checks.
        for location in actual_result:
            assert 0 <= location.percentage <= 100
