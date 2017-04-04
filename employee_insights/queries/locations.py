# local
from employee_insights.models import Location


def get_locations(session):
    """
    Get the query for retrieving all locations.

    :param session: SQLAlchemy session to use for generating the query.

    :return: Query object giving the number of all employees for a company.
             The following columns are available:

                - continent
                - country
                - state
                - city
    """
    return ( session
.       query   (Location.continent)
.       union   (session.query(Location.country_description))
.       union   (session.query(Location.state_description))
.       union   (session.query(Location.city_description))
    )
