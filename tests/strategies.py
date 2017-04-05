# std
from functools import partial
import datetime
import os
import io
import csv
# 3rd party
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from hypothesis import strategies as st
from hypothesis.extra.datetime import dates
from faker import Faker
faker = Faker()
faker.job_title = faker.job
faker.company_name = faker.company
import inflect
inflect = inflect.engine()
import stringcase
from neobunch import NeoBunch as Bunch
import yaml
# local
from employee_insights.models import *


class EmployeeData(object):

    def __init__(self, locations, job_titles, companies, employees):
        self.locations = locations
        self.job_titles = job_titles
        self.companies = companies
        self.employees = employees

    def __repr__(self):
        tmp = {
            name: [dict(x) for x in value]
            for name, value
            in self.__dict__.items()
        }
        return yaml.dump(tmp)

    def items(self):
        return self.__dict__.items()


non_empty_lists = partial(st.lists, min_size=1)


POOL_SIZE = 50
MAX_LOCATIONS = 5
MAX_JOB_TITLES = 10
MAX_COMPANIES = 15
MAX_EMPLOYEES = 20


# use faker to create some fake object pools, any data would probably do
# here, however for debugging it's nice if these fields contain something
# that looks like real data.
fake_object_pools = {
    x: [{x: getattr(faker, x)()} for _ in range(POOL_SIZE)]
    for x in ('job_title', 'company_name', 'first_name', 'last_name')
}

# for most test data the Faker module can be used, however there are not
# really any nice fake locations in this package, so load these from a
# pre-generated file.
__dir__ = os.path.dirname(__file__)
with open(os.path.join(__dir__, 'data/locations.csv'), encoding='utf-8') as f:
    fake_object_pools['location'] = list(csv.DictReader(f, delimiter=','))


min_age, max_age = 16, 100
min_year, max_year = (datetime.date.today().year - x for x in (max_age, min_age))
dates_of_birth = partial(dates, min_year, max_year)


def draw_items_from_pool(draw, which, min_size, max_size,
                         get_id_column_name=lambda x: x + '_id'):
    """
    Draw a list of NeoBunch containing example items from one of the pools of
    objects.

    NeoBunch is a subclass of dict where the items can be accessed like
    attributes and can be used both like an object and like a dict.

    :param draw: Callable for drawing examples from strategies.
    :param which: The name of the object pool to sample from.
    :param min_size: The minimum number of items to draw
    :param max_size: The maximum number of items to draw

    :return: List of dicts containing data for requested example items.
    """
    pool = fake_object_pools[which]
    strategy = st.sampled_from(pool)
    items = draw(non_empty_lists(strategy, min_size=min_size, max_size=max_size))
    return [
        Bunch(
            # generate id - autoincrement starts from 1
            {get_id_column_name(which): i + 1},
            **x,
        )
        for i, x in enumerate(items)
    ]


@st.composite
def employees(draw, locations, job_titles, companies):
    """
    Returns a strategy which generates a NeoBunch containing data describing an
    employee instance.

    NeoBunch is a subclass of dict where the items can be accessed like
    attributes and can be used both like an object and like a dict.

    :param draw: Callable for drawing examples from strategies.
    :param locations: The available locations drawn by hypothesis.
    :param job_titles: The available job titles drawn by hypothesis.
    :param companies: The available companies drawn by hypothesis.

    :return: Strategy for generating a ``dict`` with employee data.
    """
    def draw_name(which):
        pool = fake_object_pools[which]
        strategy = st.sampled_from(pool)
        return draw(strategy)[which]

    def draw_id(which):
        return draw(st.integers(min_value=1, max_value=len(which)))

    return Bunch(
        first_name=draw_name('first_name'),
        last_name=draw_name('last_name'),
        date_of_birth=draw(dates_of_birth()),
        location_id=draw_id(locations),
        job_title_id=draw_id(job_titles),
        company_id=draw_id(companies),
    )


@st.composite
def lists_of_employees(draw, locations, job_titles, companies, min_size, max_size):
    """
    Returns a strategy which generates a list of NeoBunch containing data
    describing an employee instances.

    NeoBunch is a subclass of dict where the items can be accessed like
    attributes and can be used both like an object and like a dict.

    :param draw: Callable for drawing examples from strategies.
    :param locations: The available locations drawn by hypothesis.
    :param job_titles: The available job titles drawn by hypothesis.
    :param companies: The available companies drawn by hypothesis.
    :param min_size: The minimum number of employee instances to generate.
    :param max_size: The maximum number of employee instances to generate.

    :return: Strategy for generating a ``dict`` with employee data.
    """
    strategy = employees(locations, job_titles, companies)
    items = draw(non_empty_lists(strategy, min_size=min_size, max_size=max_size))
    return [
        # generate id - autoincrement starts from 1
        Bunch(employee_id=i+1, **x)
        for i, x in enumerate(items)
    ]


@st.composite
def employee_data(draw, min_employees=1, max_employees=MAX_EMPLOYEES,
                        min_companies=1, max_companies=MAX_COMPANIES,
                        min_job_titles=1, max_job_titles=MAX_JOB_TITLES,
                        min_locations=1, max_locations=MAX_LOCATIONS):
    """
    Returns a strategy which generates a list of NeoBunch containing data
    describing an employee instances.

    NeoBunch is a subclass of dict where the items can be accessed like
    attributes and can be used both like an object and like a dict.

    :param draw: Callable for drawing examples from strategies.

    :return:
    """
    locations = draw_items_from_pool(draw, 'location',
                                     min_size=min_locations, max_size=max_locations)
    job_titles = draw_items_from_pool(draw, 'job_title',
                                      min_size=min_job_titles, max_size=max_job_titles)

    # for company we need to transform company_name to company for generating
    # the id column name.
    def get_company_id(item):
        return item.replace('_name', '') + '_id'
    companies = draw_items_from_pool(draw, 'company_name', min_size=min_companies,
                                     max_size=max_companies, get_id_column_name=get_company_id)

    strategy = lists_of_employees(locations, job_titles, companies,
                                  min_size=min_employees, max_size=max_employees)
    employees = draw(strategy)

    return EmployeeData(locations, job_titles, companies, employees)


def import_data(data, session):
    """
    Import employee data into the database using the given session object.

    :param data: Employee data to import, see ``employee_data``
    :param session: SQLAlchemy session object
    """
    items = []

    for table_name, table_data in data.items():

        table_name_singular = inflect.singular_noun(table_name)
        table_name_pascal = stringcase.pascalcase(table_name_singular)

        factory = globals()[table_name_pascal]
        items += [
            # construct an instance of the Model, ignoring id columns since
            # these are auto incremented in the database.
            factory(**{
                name: value
                for name, value in construct_args.items()
                # don't add primary key
                if name != table_name_singular + '_id'
            })
            for construct_args in table_data
        ]

    session.add_all(items)
    session.flush()
    session.commit()


@st.composite
def employee_databases(draw, url='sqlite:///:memory:',
                       min_employees=1, max_employees=MAX_EMPLOYEES,
                       min_companies=1, max_companies=MAX_COMPANIES,
                       min_job_titles=1, max_job_titles=MAX_JOB_TITLES,
                       min_locations=1, max_locations=MAX_LOCATIONS):
    """
    Return a strategy that will generate test instances of the employee
    database.

    :param draw: Callable for drawing examples from strategies.
    :param url: SQLAlchemy url for connecting to the test database.

    :return: Strategy that will generate employee data and a SQLAlchemy
             database with employee schema created and data imported. The
             strategy generates a tuple of (employee_data, SQLAlchemy session)
    """
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    data = draw(employee_data(min_employees, max_employees,
                              min_companies, max_companies,
                              min_job_titles, max_job_titles,
                              min_locations, max_locations))

    import_data(data, session)

    return data, session
