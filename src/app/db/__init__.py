import os

from sqlalchemy import create_engine, orm

from app.config import DB_FILEPATH

from .models import Base

if not DB_FILEPATH:
    raise KeyError("'DB_FILEPATH' env var not set")
if not os.path.exists(DB_FILEPATH):
    raise FileNotFoundError(f"File at '{DB_FILEPATH}' does not exist")

engine = create_engine(f"sqlite:///{DB_FILEPATH}", echo=True)
Session = orm.sessionmaker(bind=engine)

Base.metadata.create_all(engine)
