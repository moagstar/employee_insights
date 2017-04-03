# std
from functools import partial
from codecs import getreader
# 3rd party
from flask import jsonify, Blueprint, request, Response
# local
from employee_insights.database import session
from employee_insights.queries import *
from employee_insights.serializer import CsvSerializer


def make_response(query, **fields):
    """

    :param result:
    :param fields:

    :return:
    """
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


@api.route('/employees/percentage_older_than_average/<n_years>')
def employees_percentage_older_than_average(n_years):
    """
    """
    query = partial(get_employees_percentage_older_than_average, n_years=n_years)
    return make_response(
        query,
        company_name=str,
        average_employee_age=float,
        percentage_older=float,
    )


@api.route('/employees/percentage_by_location/<min_percentage>/<continent>/<country>/<state>/<city>')
@api.route('/employees/percentage_by_location/<min_percentage>/<continent>/<country>/<state>')
@api.route('/employees/percentage_by_location/<min_percentage>/<continent>/<country>')
@api.route('/employees/percentage_by_location/<min_percentage>/<continent>')
def employees_percentage_by_location(min_percentage, continent, country=None, state=None, city=None):
    """
    :return:
    """
    query = partial(get_employees_percentage_by_location, continent=continent,
                    country=country, state=state, city=city,
                    min_percentage=min_percentage)
    return make_response(
        query,
        company_name=str,
        location=str,
        percentage=float,
    )


@api.route('/employees/percentage_per_job_title')
def employees_percentage_per_job_title():
    """
    """
    return make_response(
        get_employees_percentage_per_job_title,
        company_name=str,
        job_title=str,
        percentage=float,
    )


@api.route('/employees', methods=['POST'])
def employees_post():
    """
    :return:
    """
    fileobj = getreader('utf-8')(request.files['file'].stream)
    CsvSerializer(session).load(fileobj)
    return Response(status=200)


@api.route('/employees')
def employees_get():
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
