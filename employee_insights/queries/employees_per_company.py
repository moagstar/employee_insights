# 3rd party
from sqlalchemy import func
# local
from employee_insights.models import Company, Employee


def get_employees_per_company(session):
    """
    Get the query for retrieving the number of all employees per company.

    :param session: SQLAlchemy session to use for generating the query.

    :return: Query object giving the number of all employees for a company.
             The following columns are available:

                - company_name
                - employee_count
    """
    return ( session
.       query       (Company.company_id, func.count().label('total'))
.       join        (Employee)
.       group_by    (Company.company_id)
    )