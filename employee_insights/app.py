# 3rd party
from flask import Flask, send_from_directory
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Subgroup, Link
# local
from employee_insights.api import api
from employee_insights.views import views


app = Flask(__name__)


@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)


app.register_blueprint(views)
app.register_blueprint(api, url_prefix='/api')


Bootstrap(app)


nav = Nav()


@nav.navigation()
def mynavbar():
    return Navbar(
        'Employee Insights',
        View('Home', 'views.index'),
        View('Age', 'views.age'),
        View('Location', 'views.location'),
        View('Job Title', 'views.job_title'),
        Subgroup(
            'Data',
            View('Import', 'views.import_'),
            Link('Export', '/export'),
        )
    )


nav.init_app(app)


if __name__ == '__main__':
    app.run()

