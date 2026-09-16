import os

import pandas as pd
from sqlalchemy import create_engine, insert, orm, select
from sqlalchemy.sql.selectable import TypedReturnsRows

from app.config import DB_FILEPATH

from .models import Base, Log, Supervisor

if not DB_FILEPATH:
    raise KeyError("'DB_FILEPATH' env var not set")
if not os.path.exists(DB_FILEPATH):
    raise FileNotFoundError(f"File at '{DB_FILEPATH}' does not exist")

engine = create_engine(f"sqlite:///{DB_FILEPATH}", echo=True)
Session = orm.sessionmaker(bind=engine)

Base.metadata.create_all(engine)


class DatabaseManager:
    @classmethod
    def query(cls, stmt: TypedReturnsRows):
        with Session() as session:
            return session.scalars(stmt).all()

    @classmethod
    def insert_one(cls, model: Base):
        with Session() as session:
            session.add(model)
            session.commit()

    @classmethod
    def insert_many(cls, model_type: type[Base], data: list):
        with Session() as session:
            stmt = insert(model_type).returning(model_type)
            session.execute(stmt, data)
            session.commit()

    @classmethod
    def get_logs_dataframe(cls) -> pd.DataFrame:
        stmt = select(Log, Supervisor).join(
            Supervisor,
            Log.supervisor_id == Supervisor.id,
        )
        return pd.read_sql_query(stmt, con=engine)
