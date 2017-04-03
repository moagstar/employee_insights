# std
import io
import datetime
# 3rd party
from hypothesis import given, settings
import hypothesis.extra.datetime as st_dt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# local
from employee_insights.models import Base
from employee_insights.serializer import CsvSerializer
from test_strategies import employee_databases


@settings(max_examples=50)
@given(employee_databases(min_employees=0), st_dt.datetimes(min_year=datetime.date.today().year))
def test_serializer(employee_database, timestamp):

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
