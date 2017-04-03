# 3rd party
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# local
from employee_insights.models import Base


engine = create_engine('sqlite:///employee_insights.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
