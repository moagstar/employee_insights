# 3rd party
from sqlalchemy import func, case
# local
from employee_insights.models import Employee, Company
from employee_insights.queries.company_statistics import get_company_statistics


def get_is_older_case(company_statistics, years):
    """
    Get the case clause or determining if an employee is ``years`` older
    than the company-wide average.

    :param company_statistics: Sub-query containing company_statistics
    :param years: This many years older than the company-wide average.

    :return: Case clause which gives 1.0 for an employee that is years older
             than the company-wide average, otherwise 0.0
    """
    when = (Employee.age - years) > company_statistics.c.average_employee_age
    return case([(when, 1.0)], else_=0.0)


def get_employees_percentage_older_than_average(session, years):
    """
    Get the query for retrieving the percentage of all employees per company
    that are specified number of years older than the company-wide average.

    :param session: SQLAlchemy session to use for generating the query.
    :param years: Query the percentage of employees that are this many years
                    older than the company-wide average.

    :return: Query object giving the percentage of all employees for a company
             that are years older than the company-wide average. The following
             columns are available:

                - company_id
                - company_name
                - average_employee_age
                - percentage_older

    """
    company_statistics = get_company_statistics(session).subquery()
    is_older = get_is_older_case(company_statistics, years)
    label = 'percentage_older'
    return (session
.       query       (
                     Company.company_id,
                     Company.company_name,
                     company_statistics.c.average_employee_age,
                     (func.sum(is_older) / func.count() * 100).label(label),
                    )
.       join        (Employee.company)
.       join        (company_statistics)
.       group_by    (Employee.company_id)
    )
