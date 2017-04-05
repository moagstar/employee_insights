# std
from functools import partial
from codecs import getreader
from contextlib import closing
# 3rd party
from flask import jsonify, Blueprint, request, Response
# local
from employee_insights import database
from employee_insights.queries import *
from employee_insights.serializer import CsvSerializer


def make_response(query, **fields):
    """
    Create a json response from a SQLAlchemy query.

    :param query: The SQLAlchemy query to get the json response for.
    :param fields: The fields which should be included in the json.

    :return: Json response with a list of dictionaries which are the records
             from the result set of ``query``.
    """
    with closing(database.get_session()) as session:
        result = query(session)
        result_list = [
            {
                field_name: field_type(getattr(x, field_name))
                for field_name, field_type in fields.items()
            }
            for x in result
        ]
    return jsonify(result_list)


api = Blueprint('api', __name__)


@api.route('/employees/percentage_older_than_average')
def employees_percentage_older_than_average():
    """
    GET the percentage of employees that a n years older than the company average.
    """
    years = request.args.get('years') or 0

    query = partial(get_employees_percentage_older_than_average, years=years)
    return make_response(
        query,
        company_name=str,
        average_employee_age=int,
        percentage_older=int,
    )


@api.route('/employees/percentage_by_location')
def employees_percentage_by_location():
    """
    GET the percentage of employees per company at a particular location.
    """
    min_percentage = request.args.get('min_percentage') or 0
    location = request.args.get('location') or ''

    if location:

        query = partial(get_employees_percentage_by_location,
                        location=location, min_percentage=min_percentage)

        return make_response(
            query,
            company_name=str,
            location=str,
            percentage=int,
        )

    return Response('expected location parameter', 400)


@api.route('/employees/percentage_per_job_title')
def employees_percentage_per_job_title():
    """
    GET the percentage of employees per company with a particular job title.
    """
    return make_response(
        get_employees_percentage_per_job_title,
        company_name=str,
        job_title=str,
        percentage=lambda x: round(float(x), 2),
    )


@api.route('/employees', methods=['POST'])
def employees_post():
    """
    Handle uploading of a csv file with employee data.
    """
    fileobj = getreader('utf-8')(request.files['file'].stream)
    with closing(database.get_session()) as session:
        CsvSerializer(session).load(fileobj)
    return Response(status=200)


@api.route('/employees')
def employees_get():
    """
    GET all the employees.
    """
    return make_response(
        get_employees,
        employee_id=int,
        job_title=str,
        continent=str,
        country=str,
        state=str,
        city=str,
        age=float,
        first_name=str,
        last_name=str,
        company_name=str,
    )


@api.route('/locations')
def locations_get():
    """
    GET all the locations.
    """
    return make_response(
        get_locations,
        continent=str,
        country=str,
        state=str,
        city=str
    )