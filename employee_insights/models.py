from sqlalchemy import Column, Integer, String, Date, ForeignKey, Table, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_repr import RepresentableBase
from sqlalchemy.ext.hybrid import hybrid_property


Base = declarative_base(cls=RepresentableBase)


class Company(Base):

    __tablename__ = 'company'
    __table_args__ = {'sqlite_autoincrement': True}

    company_id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String)
    employees = relationship('Employee', back_populates='company')


class Location(Base):

    __tablename__ = 'location'
    __table_args__ = {'sqlite_autoincrement': True}

    location_id = Column(Integer, primary_key=True, autoincrement=True)
    continent = Column(String)
    country = Column(String)
    state = Column(String)
    city = Column(String)
    employees = relationship('Employee', back_populates='location')

    @hybrid_property
    def country_description(self):
        return self.continent + "/" + self.country

    @hybrid_property
    def state_description(self):
        return self.continent + "/" + self.country + "/" + self.state

    @hybrid_property
    def city_description(self):
        return func.rtrim(self.continent + "/" + self.country + "/" +
                          self.state + "/" + self.city, '/')


class JobTitle(Base):

    __tablename__ = 'job_title'
    __table_args__ = {'sqlite_autoincrement': True}

    job_title_id = Column(Integer, primary_key=True, autoincrement=True)
    job_title = Column(String)
    employees = relationship('Employee', back_populates='job_title')


NOW = "now"


class Employee(Base):

    __tablename__ = 'employee'
    __table_args__ = {'sqlite_autoincrement': True}

    employee_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String)
    last_name = Column(String)
    date_of_birth = Column(Date)

    company_id = Column(Integer, ForeignKey('company.company_id'))
    company = relationship('Company', back_populates='employees')

    job_title_id = Column(Integer, ForeignKey('job_title.job_title_id'))
    job_title = relationship('JobTitle', back_populates='employees')

    location_id = Column(Integer, ForeignKey('location.location_id'))
    location = relationship('Location', back_populates='employees')

    @hybrid_property
    def age(self):
        return (func.julianday(NOW) - func.julianday(self.date_of_birth)) / 365.25
