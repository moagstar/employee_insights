# 3rd party
from hypothesis import strategies as st, given, settings
import pytest
# local
from tests.fixtures import page
from tests.common import perform_integration_test
from tests.strategies import employee_data
from tests.test_2_unit_location import get_expected, get_test_location


@settings(max_examples=10)
@given(data=employee_data(), draw=st.data(),
       min_percentage=st.integers(min_value=0, max_value=100))
def test_integration_location(data, draw, min_percentage, page):
    """
    Verify that getting the percentage of employees at a particular location works end to
    end (load page -> set params -> query -> result).

    :param data: Employee test data
    :param draw: Hypothesis data strategy for interactively drawing examples.
    :param min_percentage: The minimum percentage to filter results by.
    :param page: Capybara page object.
    """
    location = get_test_location(draw.draw, data)

    compare_functions = [
        lambda x, y: x.company_name == y.company_name,
        lambda x, y: x.location == y.location,
        lambda x, y: pytest.approx(float(x.percentage), 0.1) == float(y.percentage),
    ]

    perform_integration_test(data, page, 'location', get_expected, compare_functions,
                             min_percentage=min_percentage, location=location)
