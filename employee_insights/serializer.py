# std
import csv
import collections
import datetime
import frozendict
import contextlib
from functools import partial
# 3rd party
import attr
# local
from employee_insights.models import *


@attr.s
class CsvRecord(object):
    """
    Represents a record containing employee information from the csv file.
    """
    record_id = attr.ib()
    job_title = attr.ib()
    continent = attr.ib()
    country = attr.ib()
    state = attr.ib()
    city = attr.ib()
    age = attr.ib()
    first_name = attr.ib()
    last_name = attr.ib()
    company_name = attr.ib()
    timestamp = attr.ib()

    @property
    def date_of_birth(self):
        """
        Calculate the employee date of birth from the record timestamp and
        the
        """
        return self.timestamp - datetime.timedelta(days=float(self.age) * 365.25)


class CsvSerializer(object):

    def __init__(self, session):
        self.session = session
        self.store = {}

    def load(self, fileobj, timestamp=datetime.datetime.now()):

        self.store = {}

        reader = csv.reader(fileobj, delimiter=',')
        next(reader)  # skip headers

        for employee_id, record in enumerate(reader):

            csv_record = CsvRecord(*record, timestamp=timestamp)

            job_title_id = self._factory(JobTitle, csv_record)
            company_id = self._factory(Company, csv_record)
            location_id = self._factory(Location, csv_record)

            extra_fields = dict(
                location_id=location_id,
                company_id=company_id,
                job_title_id=job_title_id,
                date_of_birth=csv_record.date_of_birth)
            self._factory(Employee, csv_record, lambda x: x.record_id, **extra_fields)

        for cls_store in self.store.values():
            self.session.add_all(x for x, _ in cls_store.values())
        self.session.flush()
        self.session.commit()

    def dump(self, fileobj, timestamp=datetime.datetime.now()):

        fileobj.write(',Job Title,Location,Location,Location,Location,Age,first_name,last_name,Company\n')
        writer = csv.writer(fileobj, delimiter=',', lineterminator='\n')

        factory = partial(self._csv_record_factory, timestamp=timestamp)
        employees = self.session.query(Employee)
        employees = map(factory, employees)

        for employee in employees:
            writer.writerow(employee)

    def _csv_record_factory(self, employee, timestamp):
        with contextlib.suppress(Exception):
            return [
                employee.employee_id,
                employee.job_title.job_title,
                employee.location.continent,
                employee.location.country,
                employee.location.state,
                employee.location.city,
                (timestamp.date() - employee.date_of_birth).days / 365.25,
                employee.first_name,
                employee.last_name,
                employee.company.company_name,
            ]
        return []

    def _factory(self, cls, csv_record, key=None, **extra_fields):

        fields = dict(csv_record.__dict__, **extra_fields)
        fields = {
            name: value
            for name, value in fields.items()
            if name in cls.__table__.columns
        }

        if cls not in self.store:
            self.store[cls] = collections.OrderedDict()
        cls_store = self.store[cls]

        store_key = frozendict.frozendict(fields) if key is None else key(csv_record)
        if store_key not in cls_store:
            item = cls(**fields)
            cls_store[store_key] = item, len(cls_store) + 1

        _, id = cls_store[store_key]
        return id
