# std
import io
import datetime
from codecs import getwriter
from contextlib import closing
# 3rd party
from flask import render_template, send_file, Blueprint
# local
from employee_insights.serializer import CsvSerializer
from employee_insights import database
from employee_insights.queries import get_locations


views = Blueprint('views', __name__)


@views.route('/age')
def age():
    return render_template('age.html')


@views.route('/export')
def export():
    fileobj = getwriter('utf-8')(io.BytesIO())
    with closing(database.get_session()) as session:
        CsvSerializer(session).dump(fileobj)
    fileobj.seek(0)
    filename = datetime.datetime.now().strftime('%Y%m%d_%H%M%S.csv')
    return send_file(fileobj, as_attachment=True,
                     attachment_filename=filename, mimetype='text/csv')


@views.route('/import')
def import_():
    return render_template('import.html')


@views.route('/')
def index():
    return render_template('index.html')


@views.route('/job_title')
def job_title():
    return render_template('job_title.html')


@views.route('/location')
def location():
    with closing(database.get_session()) as session:
        locations = [x[0] for x in get_locations(session)]
    return render_template('location.html', locations=locations)
