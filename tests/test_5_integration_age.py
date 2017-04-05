# # std
# import os
# # compatibility
# import mock
# import contextlib2 as contextlib
# # 3rd party
# from hypothesis.stateful import RuleBasedStateMachine, rule, precondition
# from hypothesis import strategies as st, assume, settings
# import capybara
# from capybara.dsl import page
# # local
# from employee_insights.app import app
from fixtures import page


def test_integration_age(page):
    page.visit('age')
