# 3rd party
from sqlalchemy import func, case
# local
from employee_insights.models import Employee, Company, Location, JobTitle


def get_company_statistics(session):
    """
    Retrieve a query for retrieving company aggregated statistics.

    :param session: SQLAlchemy session to use for generating the query.

    :return: Query object giving the percentage of all employees for a company
             that are n_years older than the company-wide average. The following
             columns are available:

                - company_name
                - average_employee_age
    """
    average_employee_age = func.avg(Employee.age).label('average_employee_age')
    return (session
.       query       (Employee.company_id, average_employee_age)
.       group_by    (Employee.company_id)
    )


def get_is_older_case(company_statistics, n_years):
    """
    Get the case clause or determining if an employee is ``n_years`` older
    than the company-wide average.

    :param company_statistics: Sub-query containing company_statistics
    :param n_years: This many years older than the company-wide average.

    :return: Case clause which gives 1.0 for an employee that is n_years older
             than the company-wide average, otherwise 0.0
    """
    when = (Employee.age - n_years) > company_statistics.c.average_employee_age
    return case([(when, 1.0)], else_=0.0)


def get_employees_percentage_older_than_average(session, n_years):
    """
    Get the query for retrieving the percentage of all employees per company
    that are specified number of years older than the company-wide average.

    :param session: SQLAlchemy session to use for generating the query.
    :param n_years: Query the percentage of employees that are this many years
                    older than the company-wide average.

    :return: Query object giving the percentage of all employees for a company
             that are n_years older than the company-wide average. The following
             columns are available:

                - company_id
                - company_name
                - average_employee_age
                - percentage_older

    """
    company_statistics = get_company_statistics(session).subquery()
    is_older = get_is_older_case(company_statistics, n_years)
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


def get_employees_percentage_by_location(session, continent, country, state, city, min_percentage):
    """
    Get the query for retrieving the percentage of employees of a company at a
    particular location, filtered by a minimum percentage of employees.

    :param session: SQLAlchemy session to use for generating the query.
    :param continent:
    :param country:
    :param state:
    :param city:
    :param min_percentage:

    :return: Query object giving the percentage of employees of a company at a
             particular location.
             The following columns are available:

                - company_name
                - location_name
                - percentage
    """
    where = f'{continent or "%"}/{country or "%"}/{state or "%"}/{city or "%"}'.format(**locals())

    where_key = (
        Location.continent + '/' +
        Location.country + '/' +
        Location.state + '/' +
        Location.city
    )

    location_column = func.coalesce(continent, country, state, city)

    employees_per_company = get_employees_per_company(session).subquery()

    if city is not None:
        group_by = Location.continent + '/' + Location.country + '/' + Location.state + '/' + Location.city
    elif state is not None:
        group_by = Location.continent + '/' + Location.country + '/' + Location.state
    elif country is not None:
        group_by = Location.continent + '/' + Location.country
    else:
        group_by = Location.continent

    percentage = ((1.0 * func.count()) / employees_per_company.c.total * 100)

    return (session
.       query       (
                     Company.company_id,
                     Company.company_name,
                     group_by.label('location'),
                     percentage.label('percentage'),
                    )
.       join        (Employee)
.       join        (Location)
.       join        (employees_per_company,
                     employees_per_company.c.company_id == Company.company_id)
.       filter      (where_key.like(where))
.       group_by    (Employee.company_id, group_by)
.       having      (percentage > min_percentage)
    )


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
