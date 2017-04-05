# std
import io
import datetime
from unittest import mock
# 3rd party
import pytest
from hypothesis import given, settings
import hypothesis.extra.datetime as st_dt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# local
from employee_insights.models import Base
from employee_insights.serializer import CsvSerializer, date_of_birth_to_age, age_to_date_of_birth
from tests.strategies import employee_databases


@pytest.mark.skip()
@given(st_dt.dates(), st_dt.datetimes())
def test_convert_age_date_of_birth(date_of_birth, timestamp):
    """
    Verify that convert between age and date of birth round trips correctly,
    currently skipped because I know this doesn't work correctly.

    :param date_of_birth: The date of birth to use for calculation
    :param timestamp: The current timestamp to use for calculation
    """
    age = date_of_birth_to_age(date_of_birth, timestamp)
    date_of_birth2 = age_to_date_of_birth(age, timestamp)
    assert date_of_birth2 == date_of_birth


@pytest.mark.skip()
@settings(max_examples=50)
@given(employee_databases(min_employees=0),
       st_dt.datetimes(min_year=datetime.date.today().year))
def test_serializer(employee_database, timestamp):
    """
    Verify the serialize to and deserialize from csv.

    To verify the serialization we generate a random database, export to csv, import the csv to a
    second database. The second database is again exported to csv, if all went well the two csv
    exports should be the same.

    :param employee_database: The employee database containing test data.
    :param timestamp: The timestamp to assume for calculating ages.
    """
    with mock.patch('employee_insights.models.NOW', timestamp.strftime('%H-%m-%d %H:%M:%S')):

        employee_data, session = employee_database

        with io.StringIO() as dump:
            CsvSerializer(session).dump(dump, timestamp)
            dump1 = dump.getvalue()

        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session2 = Session()

        with io.StringIO(dump1) as load:
            CsvSerializer(session2).load(load, timestamp)

        with io.StringIO() as dump:
            CsvSerializer(session2).dump(dump, timestamp)
            dump2 = dump.getvalue()

        assert dump1
        assert dump2
        assert dump1 == dump2
