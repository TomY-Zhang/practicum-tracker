from datetime import date
from enum import StrEnum, auto
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from app.config import FIELD_MAP


class Column(StrEnum):
    A = auto()
    A1 = auto()
    B = auto()
    B1 = auto()
    B2 = auto()
    C = auto()


class TemplateEditor:
    def __init__(self, path: Path):
        self.reader = PdfReader(path)
        self.writer = PdfWriter()
        self.writer.append(self.reader)
        self.updates: dict[str, str] = {}

    def write_to_file(self, path: Path) -> None:
        self.writer.update_page_form_field_values(self.writer.pages[0], self.updates)
        with open(path, "wb") as f:
            self.writer.write(f)

    def update_field(self, field: str, value: str) -> None:
        self.updates[FIELD_MAP[field]] = value

    def set_first_name(self, value: str) -> None:
        self.update_field("first_name", value)

    def set_middle_name(self, value: str) -> None:
        self.update_field("middle_name", value)

    def set_last_name(self, value: str) -> None:
        self.update_field("last_name", value)

    def set_supervisor_name(self, value: str) -> None:
        self.update_field("supervisor_name", value)

    def set_work_setting_name(self, value: str) -> None:
        self.update_field("work_setting_name", value)

    def set_work_setting_address(self, value: str) -> None:
        self.update_field("work_setting_address", value)

    def set_bbs_file_number(self, value: int) -> None:
        self.update_field("bbs_file_number", str(value))

    def set_amft_check_box(self, value: bool) -> None:
        checked = "/Yes" if value else "/No"
        self.update_field("amft_check_box", checked)

    def set_amft_number(self, value: int) -> None:
        self.update_field("amft_number", str(value))

    def set_week_date(self, week_no: int, value: date) -> None:
        self.update_field(f"week_{week_no}", f"{value.month}/{value.day}")

    def set_table_cell(self, column: Column, week_no: int, value: int):
        self.update_field(f"{column}_{week_no}", str(value))

    def set_column_total(self, column: Column, value: int) -> None:
        self.update_field(f"{column}_total", str(value))
