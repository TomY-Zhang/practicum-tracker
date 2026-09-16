from sqlalchemy import ForeignKey, Index, Integer, String, text
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedColumn,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


class Associate(Base):
    __tablename__ = "associate"
    __table_args__ = (
        Index(
            "uq_associate_name", "first_name", "middle_name", "last_name", unique=True
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(30), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(30), nullable=False)
    last_name: Mapped[str] = mapped_column(String(30), nullable=False)
    bbs_file_number: Mapped[int | None] = mapped_column(Integer, unique=True)
    amft_number: Mapped[int | None] = mapped_column(Integer, unique=True)


class Supervisor(Base):
    __tablename__ = "supervisor"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    workplace_id: Mapped[int] = mapped_column(ForeignKey("workplace.id"))

    workplace: Mapped[Workplace] = relationship(back_populates="supervisor")
    logs: Mapped[list[Log]] = relationship(back_populates="supervisor")


class Workplace(Base):
    __tablename__ = "workplace"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    street: Mapped[str] = mapped_column(String(50), nullable=False)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    state: Mapped[str] = mapped_column(String(2), nullable=False)
    zipcode: Mapped[int] = mapped_column(Integer, nullable=False)

    supervisor: Mapped[Supervisor] = relationship(back_populates="workplace")


class Log(Base):
    __tablename__ = "log"

    def _int_column() -> MappedColumn:
        return mapped_column(
            Integer, nullable=False, default=0, server_default=text("0")
        )

    date: Mapped[str] = mapped_column(String(10), primary_key=True, nullable=False)
    hours_a: Mapped[int] = _int_column()
    hours_a1: Mapped[int] = _int_column()
    hours_b: Mapped[int] = _int_column()
    hours_b1: Mapped[int] = _int_column()
    hours_b2: Mapped[int] = _int_column()
    hours_c: Mapped[int] = _int_column()
    supervisor_id: Mapped[int] = mapped_column(ForeignKey("supervisor.id"))

    supervisor: Mapped[Supervisor] = relationship(back_populates="logs")
