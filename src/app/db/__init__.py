import os

import pandas as pd
from sqlalchemy import create_engine, delete, orm, select, update
from sqlalchemy.sql.selectable import TypedReturnsRows

from app.config import DB_FILE_PATH

from .models import Base, Log, Supervisor, Workplace

if not DB_FILE_PATH:
    raise KeyError("'DB_FILEPATH' env var not set")
if not os.path.exists(DB_FILE_PATH):
    raise FileNotFoundError(f"File at '{DB_FILE_PATH}' does not exist")

engine = create_engine(f"sqlite:///{DB_FILE_PATH}", echo=True)
Session = orm.sessionmaker(bind=engine)

Base.metadata.create_all(engine)


HOURS_COLUMNS = ["hours_a", "hours_a1", "hours_b", "hours_b1", "hours_b2"]


class DatabaseManager:
    def __init__(self):
        self.df = DatabaseManager.get_logs_dataframe()
        self.supervisors = DatabaseManager.get_supervisors()

    def save(cls, changes: dict):
        added = changes.get("added_rows", [])
        cls.save_added(added)

        edited = changes.get("edited_rows", {})
        cls.save_edited(edited)

        deleted = changes.get("deleted_rows", [])
        cls.save_deleted(deleted)

    def save_added(cls, added_rows: list[dict]):
        inserts = []

        for row in added_rows:
            super_name = row["name"]
            row["supervisor_id"] = cls.supervisors[super_name]
            del row["name"]
            inserts.append(Log(**row))

        if len(inserts) > 0:
            cls.insert(inserts)

    def save_edited(cls, edited_rows: dict):
        updates = []
        for df_idx, row in edited_rows.items():
            try:
                row["date"] = cls.logs_df.at[df_idx, "date"].strftime("%Y-%m-%d")
                updates.append(row)
            except KeyError:
                raise KeyError(
                    f"Failed to update log: no row at dataframe index {df_idx}"
                )

        if len(updates) > 0:
            cls.operation_many(update(Log), updates)

    def save_deleted(cls, deleted_rows: list[int]):
        deletes = []
        for df_idx in deleted_rows:
            try:
                date = cls.logs_df.at[df_idx, "date"].strftime("%Y-%m-%d")
                deletes.append(date)
            except KeyError:
                raise KeyError(
                    "Failed to delete log: no row at dataframe index {df_idx}"
                )

        if len(deletes) > 0:
            stmt = delete(Log).where(Log.date.in_(deletes))
            cls.operation_many(stmt)

    @classmethod
    def query(cls, stmt: TypedReturnsRows):
        with Session() as session:
            return session.scalars(stmt).all()

    @classmethod
    def insert(cls, data: Base | list):
        with Session() as session:
            if isinstance(data, list):
                session.add_all(data)
            else:
                session.add(data)
            session.commit()

    @classmethod
    def operation_many(cls, stmt, data: list | None = None):
        with Session() as session:
            if data:
                session.execute(stmt, data)
            else:
                session.execute(stmt)
            session.commit()

    @classmethod
    def get_logs_dataframe(cls) -> pd.DataFrame:
        stmt = select(Log, Supervisor).join(
            Supervisor,
            Log.supervisor_id == Supervisor.id,
        )
        df = pd.read_sql_query(stmt, con=engine)

        df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
        df.drop(
            columns=["supervisor_id", "id", "workplace_id"],
            inplace=True,
        )

        cls.logs_df = df
        return df

    @classmethod
    def get_supervisors(cls) -> dict[str, int]:
        supervisors = DatabaseManager.query(select(Supervisor))
        name_id_map = {s.name: s.id for s in supervisors}

        cls.supervisors = name_id_map
        return name_id_map

    @classmethod
    def get_workplaces(cls) -> dict[str, int]:
        workplaces = DatabaseManager.query(select(Workplace))
        name_id_map = {w.name: w.id for w in workplaces}

        cls.workplaces = name_id_map
        return name_id_map
