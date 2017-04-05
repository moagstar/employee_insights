# std
from itertools import zip_longest
from unittest.mock import patch
# 3rd party
from table2dicts import table2dicts
# local
from employee_insights import database


def get_company_employees(employee_data):
    """
    Returns a generator that when yielded groups employees by company.

    :param employee_data: Hypothesis generated employee database source data.

    :return: Generator which when iterated yields a tuple of
             (company, list of employees).
    """
    for company in employee_data.companies:
        is_employee = lambda x: x.company_id == company.company_id
        company_employees = list(filter(is_employee, employee_data.employees))
        if company_employees:
            yield company, company_employees


def perform_integration_test(session, page, page_name, tests, get_expected, result_columns):
    """
    Perform an integration test to verify that a query works end to end (load page -> set params ->
    show results

    :param session:
    :param page:
    :param page_name:
    :param tests:
    :param get_expected:
    :param result_columns:

    :return:
    """

    with patch('employee_insights.database.session', session):

        page.visit(page_name)

        for test in tests:

            for name, value in test:
                page.fill_in(name, value=value)

            if len(test.parameters):
                page.click_button("Go")

                actual_result = page.find("#results").text
                actual_result = table2dicts(actual_result)
                expected_result = get_expected(database.session)

                for actual, expected in zip_longest(actual_result, expected_result):
                    for result_column in result_columns:
                        assert result_column(actual) == result_column(expected)
