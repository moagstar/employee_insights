# std
from itertools import zip_longest
# 3rd party
from sqlalchemy import func, and_
# local
from employee_insights.models import Employee, Location, Company
from employee_insights.queries.employees_per_company import  get_employees_per_company


def get_employees_percentage_by_location(session, location, min_percentage):
    """
    Get the query for retrieving the percentage of employees of a company at a
    particular location, filtered by a minimum percentage of employees.

    :param session: SQLAlchemy session to use for generating the query.
    :param location: The location to get employee percentage for. This is a / sepearated list of
                     any of the following combinations:

                      - continent/country/state/city
                      - continent/country/state
                      - continent/country
                      - continent

    :param min_percentage: The minimum percentage to filter the results by.

    :return: Query object giving the percentage of employees of a company at a
             particular location.
             The following columns are available:

                - company_name
                - location
                - percentage
    """
    employees_per_company = get_employees_per_company(session).subquery()

    location = (x for x, _ in zip_longest(location.split('/'), range(4)))
    continent, country, state, city = location

    if city is not None:
        group_by = Location.continent + '/' + Location.country + '/' + Location.state + '/' + Location.city
        where = and_(Location.continent == continent, Location.country == country,
                     Location.state == state, Location.city == city)
    elif state is not None:
        group_by = Location.continent + '/' + Location.country + '/' + Location.state
        where = and_(Location.continent == continent, Location.country == country,
                     Location.state == state)
    elif country is not None:
        group_by = Location.continent + '/' + Location.country
        where = and_(Location.continent == continent, Location.country == country)
    else:
        group_by = Location.continent
        where = Location.continent == continent

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
.       filter      (where)
.       group_by    (Employee.company_id, group_by)
.       having      (percentage > float(min_percentage))
    )
