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


def age_to_date_of_birth(age, timestamp):
    days = float(age) * 365.25
    delta = datetime.timedelta(days=datetime.timedelta(days).days)
    return (timestamp - delta).date()


def date_of_birth_to_age(date_of_birth, timestamp):
    delta = timestamp.date() - date_of_birth
    delta = datetime.timedelta(days=delta.days)
    return delta.days / 365.25


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
        return age_to_date_of_birth(self.age, self.timestamp)


class CsvSerializer(object):
    """
    Serialize / Deserialize the employee insights database to and from csv.
    """

    def __init__(self, session):
        self.session = session
        self.store = {}

    def load(self, fileobj, timestamp=datetime.datetime.now()):
        """
        Load the employee insights database from a csv file.

        :param fileobj: File like object to the csv data.
        :param timestamp: The timestamp to which the csv data pertains, this is
                          for calculating the date of birth from the age.
        """

        self.store = {}

        reader = csv.reader(fileobj, delimiter=',')
        next(reader)  # skip headers

        for employee_id, record in enumerate(reader):

            csv_record = CsvRecord(*record, timestamp=timestamp)

            job_title_id = self._model_factory(JobTitle, csv_record)
            company_id = self._model_factory(Company, csv_record)
            location_id = self._model_factory(Location, csv_record)

            extra_fields = dict(
                location_id=location_id,
                company_id=company_id,
                job_title_id=job_title_id,
                date_of_birth=csv_record.date_of_birth)
            self._model_factory(Employee, csv_record, lambda x: x.record_id, **extra_fields)

        self.session.query(Location).delete()
        self.session.query(JobTitle).delete()
        self.session.query(Company).delete()
        self.session.query(Employee).delete()
        self.session.flush()
        self.session.commit()

        for cls_store in self.store.values():
            self.session.add_all(x for x, _ in cls_store.values())
        self.session.flush()
        self.session.commit()

    def dump(self, fileobj, timestamp=datetime.datetime.now()):
        """
        Dump the employee records to a csv file.

        :param fileobj: File like object where the csv records should be written.
        :param timestamp: The timestamp for calculating ages.
        """

        fileobj.write(',Job Title,Location,Location,Location,Location,Age,first_name,last_name,Company\n')
        writer = csv.writer(fileobj, delimiter=',', lineterminator='\n')

        factory = partial(self._csv_record_factory, timestamp=timestamp)
        employees = self.session.query(Employee)
        employees = map(factory, employees)

        for employee in employees:
            writer.writerow(employee)

    def _csv_record_factory(self, employee, timestamp):
        """
        Create a csv record from an Employee model and the current timestamp

        :param employee: instance of the Employee model
        :param timestamp: timestamp to use for calculating the age.

        :return: list containing the following records for exporting to csv:

                    - employee_id
                    - job_title
                    - continent
                    - country
                    - state
                    - city
                    - age
                    - first_name
                    - last_name
                    - company.company_name
        """
        result = []
        with contextlib.suppress(Exception):
            result = [
                employee.employee_id,
                employee.job_title.job_title,
                employee.location.continent,
                employee.location.country,
                employee.location.state,
                employee.location.city,
                date_of_birth_to_age(employee.date_of_birth, timestamp),
                employee.first_name,
                employee.last_name,
                employee.company.company_name,
            ]
        return result

    def _model_factory(self, model_cls, csv_record, key=None, **extra_fields):
        """
        Create an instance of a model (``model_cls``) from a csv record.

        All fields from the csv record that are also present in the model class
        are put into a dictionary with the additional fields and then used to
        instantiate the model class as keyword arguments.

        :param model_cls: The model class to instantiate.
        :param csv_record: Record containing employee data from the input csv
        :param key: Callable which is used to retrieve the key from csv_record
        :param extra_fields: Extra fields which should be used to instantiate
                             the class.

        :return: An instance of ``model_cls`` created with data from csv_recod
        """

        fields = dict(csv_record.__dict__, **extra_fields)
        fields = {
            name: value
            for name, value in fields.items()
            if name in model_cls.__table__.columns
        }

        if model_cls not in self.store:
            self.store[model_cls] = collections.OrderedDict()
        cls_store = self.store[model_cls]

        store_key = frozendict.frozendict(fields) if key is None else key(csv_record)
        if store_key not in cls_store:
            item = model_cls(**fields)
            cls_store[store_key] = item, len(cls_store) + 1

        _, id = cls_store[store_key]
        return id
