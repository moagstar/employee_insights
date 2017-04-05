# 3rd party
from hypothesis import strategies as st, given, settings
import pytest
# local
from tests.fixtures import page
from tests.common import perform_integration_test
from tests.strategies import employee_data
from tests.test_1_unit_age import get_expected


@settings(max_examples=10)
@given(data=employee_data(), years=st.integers(min_value=0, max_value=50))
def test_integration_age(data, years, page):
    """
    Verify that getting the percentage of employees older than the company average works end to
    end (load page -> set params -> query -> result).

    :param data: Employee test data.
    :param years: The number of years to fill in the interface.
    :param page: The capybara page with the age view loaded.
    """
    compare_functions = [
        lambda x, y: x.company_name == y.company_name,
        lambda x, y: pytest.approx(int(x.average_employee_age), 1) == int(y.average_employee_age),
        lambda x, y: pytest.approx(int(x.percentage_older), 1) == int(y.percentage_older),
    ]
    perform_integration_test(data, page, 'age', get_expected,
                             compare_functions, years=years)
