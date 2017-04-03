# std
from functools import partial
# 3rd party
from flask import Flask, jsonify, request
from hypothesis.types import RandomWithSeed
# local
from queries import *
#from db import create_database
from test_strategies import employee_databases


#session = create_database(create_all=True)
st_employee_database = employee_databases(
    min_employees=25, max_employees=25,
    min_companies=5, max_companies=5,
    min_job_titles=15, max_job_titles=15,
    min_locations=10, max_locations=10,
    url='sqlite:///employees.db'
)
employee_data, session = st_employee_database.example()
app = Flask(__name__)


def make_response(query, **fields):
    """

    :param result:
    :param fields:

    :return:
    """
    # TODO : Would be good to have this streaming for large result sets.

    session_to_use = session
    debug_seed = request.args.get('debug_seed')
    if debug_seed is not None:
        _, session_to_use = st_employee_database.example(RandomWithSeed(debug_seed))

    result = query(session_to_use)
    result_list = [
        {
            field_name: field_type(getattr(x, field_name))
            for field_name, field_type in fields.items()
        }
        for x in result
    ]
    return jsonify(result_list)


@app.route('/employees/percentage_older_than_average/<n_years>')
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


@app.route('/employees/percentage_by_location/<min_percentage>/<continent>/<country>/<state>/<city>')
@app.route('/employees/percentage_by_location/<min_percentage>/<continent>/<country>/<state>')
@app.route('/employees/percentage_by_location/<min_percentage>/<continent>/<country>')
@app.route('/employees/percentage_by_location/<min_percentage>/<continent>')
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


@app.route('/employees/percentage_per_job_title')
def employees_percentage_per_job_title():
    """
    """
    return make_response(
        get_employees_percentage_per_job_title,
        company_name=str,
        job_title=str,
        percentage=float,
    )


# @hug.put('/employees')
@app.route('/employees', methods=['PUT'])
def employees(csv):
    """
    :param csv:
    :return:
    """


if __name__ == '__main__':
    app.run()
