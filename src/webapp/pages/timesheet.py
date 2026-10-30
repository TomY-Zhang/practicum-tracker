from datetime import date, datetime, timedelta

import streamlit as st
from pandas import DataFrame, Timestamp

from webapp.backend import DatabaseManager
from webapp.backend.models import Supervisor, Workplace
from webapp.backend.pdf import Column, TemplateEditor
from webapp.config import GENERATED_PDF_NAME, TEMPLATE_FILE_PATH

dbm = DatabaseManager()


def load_session() -> None:
    st.session_state.df = dbm.df
    st.session_state.supervisors = dbm.supervisors
    st.session_state.workplaces = dbm.workplaces
    print(st.session_state.workplaces)


@st.dialog("Add Supervisor", icon="👨‍💼")
def add_supervisor_dialog():
    with st.form("Add Supervisor Form"):
        name = st.text_input("Supervisor Name", max_chars=100)

        workplace_names: list[str] = list(st.session_state.workplaces.keys())
        workplace = st.selectbox("Workplace", workplace_names)

        if st.form_submit_button("Submit", use_container_width=True, type="primary"):
            if name and workplace:
                wp_id = st.session_state.workplaces.get(workplace)
                if wp_id:
                    DatabaseManager.insert(Supervisor(name=name, workplace_id=wp_id))
                else:
                    st.toast(
                        f"Error: unable to determine ID for workplace '{workplace}'",
                        icon="🚫",
                    )
                st.toast(f"Added new supervisor '{name}'", icon="✅")
                st.rerun()
            else:
                st.toast("Please fill out all fields", icon="🚫")


@st.dialog("Add Workplace", icon="🏢")
def add_workplace_dialog():
    with st.form("Add Workplace Form"):
        name = st.text_input("Workplace Name", max_chars=100)
        street = st.text_input("Street", max_chars=50)
        city = st.text_input("City", max_chars=50)

        cols = st.columns([1, 1])
        with cols[0]:
            state = st.text_input("State Abbreviation (e.g. CA, UT)", max_chars=2)
        with cols[1]:
            zipcode = st.text_input("Zip Code", max_chars=5)

        if st.form_submit_button("Submit", use_container_width=True, type="primary"):
            if name and street and city and state and zipcode:
                if zipcode.isnumeric():
                    DatabaseManager.insert(
                        Workplace(
                            name=name,
                            street=street,
                            city=city,
                            state=state,
                            zipcode=zipcode,
                        )
                    )
                    st.toast(f"Added new workplace '{name}'", icon="✅")
                    st.rerun()
                else:
                    st.toast("Zip code can only contain numbers", icon="🚫")
            else:
                st.toast("Please fill out all fields", icon="🚫")


@st.dialog("Save to PDF", icon="📥")
def save_pdf_dialog():
    now = datetime.now()  # noqa: DTZ005
    selected_dates = st.date_input(
        "Select a date range (up to 10 weeks)",
        help="Days in the same week as the start and end dates will be included. A week is defined as Sunday through Saturday.",
        value=(now, now),
    )

    try:
        st.download_button(
            label="Download",
            data=pdf_bytes(selected_dates),
            file_name=GENERATED_PDF_NAME,
            mime="application/pdf",
        )
    except ValueError as e:
        st.toast(str(e), icon="🚫")
    except LookupError:
        pass


def pdf_bytes(selected_dates: tuple) -> bytes:
    validate_date_range(selected_dates)
    start = get_week_start_sunday(selected_dates[0])
    end = get_week_end_saturday(selected_dates[1])

    df: DataFrame = st.session_state.df
    mask = (df["date"] >= Timestamp(start)) & (df["date"] <= Timestamp(end))
    supervisors = df.loc[mask, "name"].unique()

    template_editor = TemplateEditor(TEMPLATE_FILE_PATH)
    template_editor.set_year(start.year)
    if len(supervisors) > 1:
        raise ValueError(
            "Selected date range contains logs for multiple supervisors. Please select a date range that contains logs for only one supervisor."
        )
    elif len(supervisors) == 1:
        template_editor.set_supervisor_name(supervisors[0])

    week = 1
    column_totals = {c: 0 for c in Column}
    while start <= end:
        week_end = min(start + timedelta(days=6), end)
        mask = (df["date"] >= Timestamp(start)) & (df["date"] <= Timestamp(week_end))
        hours = df.loc[mask].sum(numeric_only=True)
        week_total = hours.sum(numeric_only=True)

        template_editor.set_week_date(week, start)
        template_editor.set_table_cell(Column.A, week, hours["hours_a"])
        template_editor.set_table_cell(Column.A1, week, hours["hours_a1"])
        template_editor.set_table_cell(Column.B, week, hours["hours_b"])
        template_editor.set_table_cell(Column.B1, week, hours["hours_b1"])
        template_editor.set_table_cell(Column.B2, week, hours["hours_b2"])
        template_editor.set_table_cell(Column.C, week, week_total)

        column_totals[Column.A] += hours["hours_a"]
        column_totals[Column.A1] += hours["hours_a1"]
        column_totals[Column.B] += hours["hours_b"]
        column_totals[Column.B1] += hours["hours_b1"]
        column_totals[Column.B2] += hours["hours_b2"]
        column_totals[Column.C] += week_total

        start += timedelta(days=7)
        week += 1

    for column, total in column_totals.items():
        template_editor.set_column_total(column, total)

    return template_editor.write_to_bytes()


def validate_date_range(selected_dates: tuple):
    if len(selected_dates) != 2:
        raise LookupError

    start = get_week_start_sunday(selected_dates[0])
    end = get_week_end_saturday(selected_dates[1])
    if end - start > timedelta(weeks=10):
        raise ValueError("Selected date range exceeds 10 weeks")


def get_week_start_sunday(dt: date) -> date:
    days_since_sunday = (dt.weekday() + 1) % 7
    return dt - timedelta(days=days_since_sunday)


def get_week_end_saturday(dt: date) -> date:
    days_until_saturday = (5 - dt.weekday()) % 7
    return dt + timedelta(days=days_until_saturday)


def render_page() -> None:
    st.title("📝 Timesheet")

    st.data_editor(
        st.session_state.df,
        column_config={
            "date": st.column_config.DateColumn(
                label="🗓️ Date",
                help="Date of log entry",
                format="YYYY-MM-DD",
                required=True,
            ),
            "name": st.column_config.SelectboxColumn(
                label="👨‍💼 Supervisor",
                help="Select your supervisor",
                options=st.session_state.supervisors.keys(),
                required=True,
            ),
            "hours_a": st.column_config.NumberColumn(
                "🫂 Direct Counseling",
                help="Individuals, groups, couples, and families",
                default=0,
            ),
            "hours_a1": st.column_config.NumberColumn(
                label="🩺 Diagnosis & Treatment",
                help="Couples, families, and children",
                default=0,
            ),
            "hours_b": st.column_config.NumberColumn(
                label="💡 Non-Clinical Experience",
                default=0,
            ),
            "hours_b1": st.column_config.NumberColumn(
                label="🕵🏻‍♂️ Supervision, Individual, & Triadic",
                default=0,
            ),
            "hours_b2": st.column_config.NumberColumn(
                label="🔍 Supervision, Group",
                default=0,
            ),
        },
        column_order=[
            "date",
            "name",
            "hours_a",
            "hours_a1",
            "hours_b",
            "hours_b1",
            "hours_b2",
        ],
        disabled=["_index"],
        key="editor",
        num_rows="dynamic",
        height="content",
    )

    cols = st.columns([15, 3, 3, 3, 2])

    with cols[-4]:
        if st.button("Add Supervisor", use_container_width=True, icon="👨‍💼"):
            add_supervisor_dialog()

    with cols[-3]:
        if st.button("Add Workplace", use_container_width=True, icon="🏢"):
            add_workplace_dialog()

    with cols[-2]:
        if st.button("Save to PDF", use_container_width=True, icon="📥"):
            save_pdf_dialog()

    with cols[-1]:
        if st.button("Save", use_container_width=True, type="primary", icon="💾"):
            dbm.save(st.session_state.editor)
            st.toast("Timesheet successfully saved", icon="✅")


load_session()
render_page()
