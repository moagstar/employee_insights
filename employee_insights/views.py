# std
import io
import datetime
from codecs import getwriter
# 3rd party
from flask import render_template, send_file
# local
from employee_insights.serializer import CsvSerializer
from employee_insights.database import session
from flask import Blueprint


views = Blueprint('views', __name__)


@views.route('/age')
def age():
    return render_template('age.html')


@views.route('/export')
def export():
    fileobj = getwriter('utf-8')(io.BytesIO())
    CsvSerializer(session).dump(fileobj)
    fileobj.seek(0)
    filename = datetime.datetime.now().strftime('%Y%m%d_%H%M%S.csv')
    return send_file(fileobj, as_attachment=True, attachment_filename=filename, mimetype='text/csv')


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
    return render_template('location.html')
