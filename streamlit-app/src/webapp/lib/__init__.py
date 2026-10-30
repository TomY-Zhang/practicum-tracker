import os

import pandas as pd
from sqlalchemy import create_engine, delete, orm, select, update
from sqlalchemy.sql.selectable import TypedReturnsRows

from webapp.config import DB_FILE_PATH

from .models import Base, Log, Supervisor, Workplace

if not DB_FILE_PATH:
    raise KeyError("'DB_FILEPATH' env var not set")
if not os.path.exists(DB_FILE_PATH):
    raise FileNotFoundError(f"File at '{DB_FILE_PATH}' does not exist")

engine = create_engine(f"sqlite:///{DB_FILE_PATH}", echo=True)
Session = orm.sessionmaker(bind=engine)

Base.metadata.create_all(engine)
