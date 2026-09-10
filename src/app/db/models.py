from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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
    supervisor: Mapped[int | None] = mapped_column(ForeignKey("supervisor.id"))
    work_setting: Mapped[int | None] = mapped_column(ForeignKey("workplace.id"))


class Supervisor(Base):
    __tablename__ = "supervisor"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)


class Workplace(Base):
    __tablename__ = "workplace"
    __table_args__ = (Index("uq_workplace", "name", "address", unique=True),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(100), nullable=False)


class Log(Base):
    __tablename__ = "log"

    date: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    hours_a: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hours_a1: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hours_b: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hours_b1: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hours_b2: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hours_c: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
