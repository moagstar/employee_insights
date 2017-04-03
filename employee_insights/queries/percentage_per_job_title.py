# 3rd party
from sqlalchemy import func
# local
from employee_insights.models import Employee, Company, JobTitle
from employee_insights.queries.employees_per_company import  get_employees_per_company


def get_employees_percentage_per_job_title(session):
    """
    Get the query for retrieving the percentage of all employees per company
    that have a particular job title.

    :param session: SQLAlchemy session to use for generating the query.

    :return: Query object giving the percentage of all employees for a company
             with a particular job title.The following columns are available:

                - company_name
                - job_title_id
                - job_title
                - percentage_with_job_title
    """
    employees_per_company = get_employees_per_company(session).subquery()
    to_float = lambda x: 1.0 * x
    return (session
.       query       (
                     Company.company_id,
                     Company.company_name,
                     Employee.job_title_id,
                     JobTitle.job_title,
                     (to_float(func.count()) / employees_per_company.c.total * 100).label('percentage'),
                    )
.       join        (Employee)
.       join        (JobTitle)
.       join        (employees_per_company,
                     employees_per_company.c.company_id == Company.company_id)
.       group_by    (Company.company_id, Employee.job_title_id)
    )
