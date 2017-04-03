# local
from employee_insights.models import Employee, JobTitle, Location, Company


def get_employees(session):
    """
    Get the query for retrieving all employees.

    :param session: SQLAlchemy session to use for generating the query.

    :return: Query object giving the number of all employees for a company.
             The following columns are available:

                - employee_id
                - job_title
                - continent
                - country
                - state
                - city
                - age
                - first_name
                - last_name
                - company_name
    """
    return ( session
.       query       (
                     Employee.employee_id,
                     JobTitle.job_title,
                     Location.continent,
                     Location.country,
                     Location.state,
                     Location.city,
                     Employee.age,
                     Employee.first_name,
                     Employee.last_name,
                     Company.company_name,
                    )
.       join        (JobTitle)
.       join        (Location)
.       join        (Company)
    )
