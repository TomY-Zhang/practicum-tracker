import pandas as pd
from sqlalchemy import delete, select, update
from sqlalchemy.sql.selectable import TypedReturnsRows

from . import Session, engine
from .models import Base, Log, Supervisor, Workplace


class DatabaseManager:
    def __init__(self):
        self.df = DatabaseManager.get_logs_as_df()
        self.supervisors = DatabaseManager.get_supervisors()
        self.workplaces = DatabaseManager.get_workplaces()

    def save(cls, changes: dict):
        edited = changes.get("edited_rows", {})
        cls.save_edited(edited)

        deleted = changes.get("deleted_rows", [])
        cls.save_deleted(deleted)

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
    def get_logs_as_df(cls) -> pd.DataFrame:
        df = pd.read_sql_query(select(Log), con=engine)
        df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
        df = df.sort_values(by="date", ascending=True)
        cls.logs_df = df
        return df

    @classmethod
    def get_supervisors(cls) -> list[Supervisor]:
        supervisors = DatabaseManager.query(select(Supervisor))
        cls.supervisors = list(supervisors)
        return cls.supervisors

    @classmethod
    def get_workplaces(cls) -> list[Workplace]:
        workplaces = DatabaseManager.query(select(Workplace))
        cls.workplaces = list(workplaces)
        return cls.workplaces
