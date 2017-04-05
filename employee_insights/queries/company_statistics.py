# 3rd party
from sqlalchemy import func
# local
from employee_insights.models import Employee


def get_company_statistics(session):
    """
    Retrieve a query for retrieving company aggregated statistics.

    :param session: SQLAlchemy session to use for generating the query.

    :return: Query object giving the percentage of all employees for a company
             that are years older than the company-wide average. The following
             columns are available:

                - company_name
                - average_employee_age
    """
    average_employee_age = func.avg(Employee.age).label('average_employee_age')
    return (session
.       query       (Employee.company_id, average_employee_age)
.       group_by    (Employee.company_id)
    )
