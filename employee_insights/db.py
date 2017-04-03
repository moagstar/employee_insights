# std
import datetime
# 3rd party
from sqlalchemy import create_engine, func, case
from sqlalchemy.orm import sessionmaker
# local
from employee_insights.models import *


def create_database(create_all=False):

    engine = create_engine('sqlite:///:memory:')
    #engine = create_engine('sqlite:///db')
    if create_all:
        Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # job_titles = [
    #     JobTitle(job_title='Senior Developer'),
    #     JobTitle(job_title='Custom Relations Assistant'),
    # ]
    #
    # microsoft_locations = [
    #     Location(continent='Europe', country='Netherlands', state='Noord Holland', city='Diemen'),
    # ]
    #
    #
    # google_locations = [
    #     Location(continent='North America', country='USA', state='California', city='San Francisco'),
    # ]
    #
    # companies = [
    #     Company(company_name='google', locations=google_locations),
    #     Company(company_name='microsoft', locations=microsoft_locations),
    # ]
    #
    # employees = [
    #     Employee(first_name='Dan', last_name='Bradburn', date_of_birth=datetime.date(1981, 7, 3), company_id=1, job_title_id=1),
    #     Employee(first_name='Fiorella', last_name='Copello', date_of_birth=datetime.date(1981, 5, 21), company_id=1, job_title_id=2),
    #     Employee(first_name='Scott', last_name='Hanselmann', date_of_birth=datetime.date(1975, 7, 3), company_id=2, job_title_id=1)
    # ]
    #
    # session.add_all(companies)
    # session.add_all(employees)
    # session.add_all(job_titles)

    session.flush()

    return session
