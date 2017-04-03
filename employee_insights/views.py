# std
import io
import datetime
from codecs import getwriter
from functools import partial
# 3rd party
from flask import Flask, jsonify, request, render_template, send_file
from hypothesis.types import RandomWithSeed
# local
from employee_insights.queries import *
from employee_insights.db import create_database
#from test_strategies import employee_databases
from employee_insights.csvimport import CsvSerializer


session = create_database(create_all=True)
# st_employee_database = employee_databases(
#     min_employees=25, max_employees=25,
#     min_companies=5, max_companies=5,
#     min_job_titles=15, max_job_titles=15,
#     min_locations=10, max_locations=10,
#     url='sqlite:///employees.db'
# )
# employee_data, session = st_employee_database.example()
# session =

app = Flask(__name__)
from flask_bootstrap import Bootstrap
Bootstrap(app)


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


@app.route('/employees', methods=['PUT'])
def employees(csv):
    """
    :param csv:
    :return:
    """


@app.route('/age')
def age():
    return render_template('age.html')


@app.route('/export_csv')
def export_csv():
    fileobj = getwriter('utf-8')(io.BytesIO())
    CsvSerializer(session).dump(fileobj)
    fileobj.seek(0)
    filename = datetime.datetime.now().strftime('%Y%m%d_%H%M%S.csv')
    return send_file(fileobj, as_attachment=True, attachment_filename=filename, mimetype='text/csv')


@app.route('/import_csv')
def import_csv():
    return render_template('import_csv.html')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/job_title')
def job_title():
    return render_template('job_title.html')


@app.route('/location')
def location():
    return render_template('location.html')


from flask_nav import Nav
from flask_nav.elements import Navbar, View, Subgroup, Link

nav = Nav()

@nav.navigation()
def mynavbar():
    return Navbar(
        'Employee Insights',
        View('Home', 'index'),
        View('Age', 'age'),
        View('Location', 'location'),
        View('Job Title', 'job_title'),
        Subgroup(
            'Data',
            View('Import', 'import_csv'),
            Link('Export', 'export_csv'),
        )
    )


nav.init_app(app)


if __name__ == '__main__':
    app.run()

