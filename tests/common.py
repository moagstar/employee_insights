# std
import time
from itertools import zip_longest
from unittest.mock import patch
# 3rd party
from table2dicts import table2dicts
from neobunch import NeoBunch as Bunch
# local
from tests.strategies import import_data


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


def perform_integration_test(data, page, page_name, get_expected, compare_functions, **parameters):
    """
    Perform an integration test to verify that a query works end to end (load page -> set params ->
    show results

    :param data: Employee test data
    :param page: The capybara page object
    :param page_name: The name of the page to load
    :param get_expected: Callable for retrieving the expected result
    :param compare_functions: iterable containing functions to use to validate the results
                              comparing the actual with the expected.
    :param **parameters: Keyword parameters which should be passed to get_expected. Also
                         defines the forms which will be filled with generated data.

    :return:
    """
    def get_url():
        return 'sqlite:///:memory:'

    def data_importer(session):
        return import_data(data, session)

    with patch('employee_insights.database.get_url', get_url), \
         patch('employee_insights.database.import_data', data_importer):

            if page.current_path != '/' + page_name:
                page.visit(page_name)

            for name, value in parameters.items():
                page.fill_in(name, value=value)

            if len(parameters):
                page.click_button("Go")

            time.sleep(0.1)

            actual_result = page.html
            actual_result = (Bunch(x) for x in table2dicts(actual_result))
            expected_result = list(get_expected(data, **parameters))

            if expected_result:
                for actual, expected in zip_longest(actual_result, expected_result):
                    for compare_function in compare_functions:
                        if not compare_function(actual, expected):
                            assert actual == expected
            else:
                expected = 'No rows'
                actual = page.find('#results').text
                assert expected in actual
