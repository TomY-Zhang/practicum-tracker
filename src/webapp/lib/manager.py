import pandas as pd
from sqlalchemy import delete, select, update
from sqlalchemy.sql.selectable import TypedReturnsRows

from . import Session, engine
from .models import Base, Log, Supervisor, Workplace


class DatabaseManager:
    def __init__(self):
        self.supervisors = self.get_supervisors()
        self.workplaces = self.get_workplaces()

        self.log_df = self.get_logs_as_df()
        self.supervisor_df = self.get_supervisors_as_df()
        self.workplace_df = self.get_workplaces_as_df()

    def save(self, model: type[Base], changes: dict):
        if model == Log:
            df = self.log_df
        else:
            df = self.supervisor_df

        self.save_edited(model, changes.get("edited_rows", {}), df)
        self.save_deleted(model, changes.get("deleted_rows", []), df)

    def save_edited(self, model: type[Base], edited_rows: dict, df: pd.DataFrame):
        updates = []
        for df_idx, row in edited_rows.items():
            try:
                row["id"] = int(df.iloc[df_idx]["id"])
                updates.append(row)
            except KeyError:
                raise KeyError(
                    f"Failed to update {model}: no row at dataframe index {df_idx}"
                )
        if len(updates) > 0:
            DatabaseManager.operation_many(update(model), updates)

    def save_deleted(
        self, model: type[Base], deleted_rows: list[int], df: pd.DataFrame
    ):
        deletes = []
        for df_idx in deleted_rows:
            try:
                log_id = int(df.iloc[df_idx]["id"])
                deletes.append(log_id)
            except KeyError:
                raise KeyError(
                    f"Failed to delete {model}: no row at dataframe index {df_idx}"
                )
        if len(deletes) > 0:
            stmt = delete(model).where(model.id.in_(deletes))
            DatabaseManager.operation_many(stmt)

    def get_logs_as_df(self) -> pd.DataFrame:
        df = pd.read_sql_query(select(Log), con=engine)
        df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
        self.log_df = df.sort_values(by="date", ascending=True)
        return self.log_df

    def get_supervisors_as_df(self) -> pd.DataFrame:
        df = pd.read_sql_query(select(Supervisor), con=engine)
        self.supervisor_df = df.sort_values(by=["name", "workplace_id"], ascending=True)
        return self.supervisor_df

    def get_workplaces_as_df(self) -> pd.DataFrame:
        df = pd.read_sql_query(select(Workplace), con=engine)
        self.workplace_df = df.sort_values(by=["name"], ascending=True)
        return self.workplace_df

    def get_supervisors(self) -> list[Supervisor]:
        self.supervisors = DatabaseManager.query(select(Supervisor))
        return self.supervisors

    def get_workplaces(self) -> list[Workplace]:
        self.workplaces = DatabaseManager.query(select(Workplace))
        return self.workplaces

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
