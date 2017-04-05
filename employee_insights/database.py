# std
import os
__dir__ = os.path.dirname(__file__)
# 3rd party
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# local
from employee_insights.models import Base


database_path = os.path.join(__dir__, '..', 'employee_insights.db')
get_url = lambda: f'sqlite:///{database_path}'
import_data = None


def get_session():
    """
    Get a SQLAlchemy session for interacting with the employee insights
    database.

    :return: SQLAlchemy session.
    """
    engine = create_engine(get_url())
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    if import_data:
        import_data(session)
    return session
