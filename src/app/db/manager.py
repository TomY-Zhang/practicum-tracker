import os

from sqlalchemy import Connection, Engine, create_engine

from app.config import DB_FILEPATH
from app.db.models import Base


class DatabaseManager:
    def __init__(self):
        self.conn: Connection | None = None

        self.engine = self.init_engine()
        self.conn = self.engine.connect()

        Base.metadata.create_all(self.engine)

    def init_engine(self) -> Engine:
        if not DB_FILEPATH:
            raise KeyError("'DB_FILEPATH' env var not set")
        if not os.path.exists(DB_FILEPATH):
            raise FileNotFoundError(f"File at '{DB_FILEPATH}' does not exist")
        return create_engine(f"sqlite:///{DB_FILEPATH}", echo=True)

    def __del__(self):
        if self.conn:
            self.conn.close()
