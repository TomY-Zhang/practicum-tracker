from datetime import date, timedelta
from enum import StrEnum

import streamlit as st
from dateutil.relativedelta import relativedelta
from pandas import Timestamp
from sqlalchemy.exc import IntegrityError

from webapp.lib.manager import DatabaseManager
from webapp.lib.models import Log, Supervisor, Workplace

dbm = DatabaseManager()
st.session_state.df = dbm.df


class ViewScope(StrEnum):
    Week = "Week"
    Month = "Month"


def update_filter_absolute():
    print("TEST")
    date = st.session_state.view_scope_date
    print("NICE", date)


def filter_view(view_date: date, scope: ViewScope):
    df = st.session_state.df

    if scope == ViewScope.Week:
        start = get_week_start_sunday(view_date)
        end = start + timedelta(days=6)
        mask = (df["date"] >= Timestamp(start)) & (df["date"] <= Timestamp(end))
    else:
        first_day_of_month = view_date.replace(day=1)
        last_day_of_month = view_date + relativedelta(days=31)
        mask = (df["date"] >= Timestamp(first_day_of_month)) & (
            df["date"] <= Timestamp(last_day_of_month)
        )

    st.session_state.df = df.loc[mask]


def supervisor_label(supervisor_id: int) -> str:
    supervisor = next(s for s in dbm.supervisors if s.id == supervisor_id)
    workplace = next(w for w in dbm.workplaces if w.id == supervisor.workplace_id)
    return f"{supervisor.name} ({workplace.name})"


def get_week_start_sunday(dt: date) -> date:
    days_since_sunday = (dt.weekday() + 1) % 7
    return dt - timedelta(days=days_since_sunday)


@st.dialog("New Log Entry", width="medium")
def log_entry_dialog():
    with st.form("log_entry_form"):
        rows = [st.columns([1, 1]) for _ in range(4)]
        with rows[0][0]:
            date = st.date_input("🗓️ Date")
        with rows[0][1]:
            supervisor = st.selectbox(
                label="👨‍💼 Supervisor",
                options=dbm.supervisors,
                format_func=lambda s: supervisor_label(s.id),
            )
        with rows[1][0]:
            hours_a = st.number_input(
                label="🫂 Direct Counseling (A)", value=0, min_value=0, max_value=24
            )
        with rows[1][1]:
            hours_b = st.number_input(
                label="💡 Non-Clinical Experience (B)",
                value=0,
                min_value=0,
                max_value=24,
            )
        with rows[2][0]:
            hours_a1 = st.number_input(
                label="🩺 Diagnosis & Treatment (A1)",
                value=0,
                min_value=0,
                max_value=24,
            )
        with rows[2][1]:
            hours_b1 = st.number_input(
                label="🕵🏻‍♂️ Supervision, Individual, Triadic (B1)",
                value=0,
                min_value=0,
                max_value=24,
            )
        with rows[3][1]:
            hours_b2 = st.number_input(
                label="🔍 Supervision, Group (B2)", value=0, min_value=0, max_value=24
            )
        if st.form_submit_button("Submit", type="primary", use_container_width=True):
            date_str = date.strftime("%Y-%m-%d")
            log = Log(
                date=date_str,
                supervisor_id=supervisor.id,
                hours_a=hours_a,
                hours_a1=hours_a1,
                hours_b=hours_b,
                hours_b1=hours_b1,
                hours_b2=hours_b2,
            )
            try:
                dbm.insert(log)
                st.toast(f"Added log entry for {date_str}.", icon="✅")
                st.rerun()
            except IntegrityError:
                st.toast(
                    f"Log entry for {date_str} already exists.",
                    icon="🚫",
                )


@st.dialog("Add Supervisor", icon="👨‍💼")
def add_supervisor_dialog():
    with st.form("Add Supervisor Form"):
        name = st.text_input("Supervisor Name", max_chars=100)
        workplace = st.selectbox(
            "Workplace", options=dbm.workplaces, format_func=lambda w: w.name
        )
        if st.form_submit_button("Submit", use_container_width=True, type="primary"):
            if name and workplace:
                try:
                    DatabaseManager.insert(
                        Supervisor(name=name, workplace_id=workplace.id)
                    )
                    st.toast(
                        f"Added new supervisor '{name}' ({workplace.name}).", icon="✅"
                    )
                    st.rerun()
                except IntegrityError:
                    st.toast(
                        f"Supervisor name '{name}' is already taken. Please enter another name.",
                        icon="🚫",
                    )
            else:
                st.toast("Please fill out all fields.", icon="🚫")


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
                    st.toast(f"Added new workplace '{name}'.", icon="✅")
                    st.rerun()
                else:
                    st.toast("Zip code can only contain numbers.", icon="🚫")
            else:
                st.toast("Please fill out all fields.", icon="🚫")


st.title("📝 Timesheet")

row1 = st.columns([88, 6, 6], gap="xsmall")
with row1[-2]:
    view_date = st.date_input(
        "Date",
        label_visibility="collapsed",
        key="view_scope_date",
        on_change=update_filter_absolute,
    )
with row1[-1]:
    view_scope = st.selectbox(
        "View Scope",
        label_visibility="collapsed",
        options=[v for v in ViewScope],
    )

filter_view(view_date, view_scope)
st.data_editor(
    st.session_state.df,
    column_config={
        "date": st.column_config.DateColumn(
            label="🗓️ Date",
            help="Log Entry Date",
            format="YYYY-MM-DD",
            disabled=True,
        ),
        "supervisor_id": st.column_config.SelectboxColumn(
            label="👨‍💼 Supervisor",
            help="Select a supervisor",
            options=(float(s.id) for s in dbm.supervisors),
            format_func=lambda id_: supervisor_label(int(id_)),
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
        "supervisor_id",
        "hours_a",
        "hours_a1",
        "hours_b",
        "hours_b1",
        "hours_b2",
    ],
    num_rows="delete",
    disabled=["_index"],
    hide_index=True,
    key="editor",
)

row2 = st.columns([71, 8, 8, 8, 5], gap="xsmall")
with row2[-4]:
    st.button(
        "Add Log Entry", on_click=log_entry_dialog, use_container_width=True, icon="📝"
    )
with row2[-3]:
    st.button(
        "Add Supervisor",
        on_click=add_supervisor_dialog,
        use_container_width=True,
        icon="👨‍💼",
    )
with row2[-2]:
    st.button(
        "Add Workplace",
        on_click=add_workplace_dialog,
        use_container_width=True,
        icon="🏢",
    )
with row2[-1]:
    if st.button("Save", type="primary", use_container_width=True):
        dbm.save(st.session_state.editor)
        st.toast("Timesheet successfully saved", icon="✅")
