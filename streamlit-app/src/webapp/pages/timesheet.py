from datetime import date, timedelta
from enum import StrEnum

import streamlit as st
from dateutil.relativedelta import relativedelta
from pandas import DataFrame, Timestamp
from sqlalchemy.exc import IntegrityError

from webapp.lib.manager import DatabaseManager
from webapp.lib.models import Log, Supervisor, Workplace

MAX_ROWS = 10
MAX_DATAFRAME_HEIGHT = 350  # 10 rows, 35 pixels per row

dbm = DatabaseManager()
st.session_state.log_df = dbm.log_df
st.session_state.sp_df = dbm.supervisor_df
st.session_state.wp_df = dbm.workplace_df
supervisors = dbm.supervisors
workplaces = dbm.workplaces


def supervisor_label(supervisor_id: int) -> str:
    supervisor = next(s for s in dbm.supervisors if s.id == supervisor_id)
    workplace = next(w for w in dbm.workplaces if w.id == supervisor.workplace_id)
    return f"{supervisor.name} ({workplace.name})"


def get_week_start_sunday(dt: date) -> date:
    days_since_sunday = (dt.weekday() + 1) % 7
    return dt - timedelta(days=days_since_sunday)


def get_df_height(df: DataFrame):
    return MAX_DATAFRAME_HEIGHT if len(df) >= MAX_ROWS else "auto"


class ViewScope(StrEnum):
    Week = "Week"
    Month = "Month"


def filter_view(view_date: date, scope: ViewScope, supervisor: Supervisor | None):
    df = st.session_state.log_df

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

    if supervisor:
        mask = mask & (df["supervisor_id"] == supervisor.id)

    st.session_state.log_df = df.loc[mask]


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
                label="🫂 Direct Counseling (A)",
                value=0.0,
                min_value=0.0,
                max_value=24.0,
            )
        with rows[1][1]:
            hours_b = st.number_input(
                label="💡 Non-Clinical Experience (B)",
                value=0.0,
                min_value=0.0,
                max_value=24.0,
            )
        with rows[2][0]:
            hours_a1 = st.number_input(
                label="🩺 Diagnosis & Treatment (A1)",
                value=0.0,
                min_value=0.0,
                max_value=24.0,
            )
        with rows[2][1]:
            hours_b1 = st.number_input(
                label="🕵🏻‍♂️ Supervision, Individual, Triadic (B1)",
                value=0.0,
                min_value=0.0,
                max_value=24.0,
            )
        with rows[3][1]:
            hours_b2 = st.number_input(
                label="🔍 Supervision, Group (B2)",
                value=0.0,
                min_value=0.0,
                max_value=24.0,
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
                    f"Log entry for {date_str} with supervisor {supervisor_label(supervisor.id)} already exists.",
                    icon="🚫",
                    duration=2,
                )


@st.dialog("Add Supervisor", icon="👨‍💼")
def add_supervisor_dialog():
    def insert_supervisor(s: Supervisor):
        try:
            dbm.insert(s)
            st.toast(f"Added new supervisor '{name}' ({workplace.name}).", icon="✅")
            st.rerun()
        except IntegrityError:
            st.toast(
                f"Supervisor name '{name}' is already taken. Please enter another name.",
                icon="🚫",
                duration=2,
            )

    with st.form("Add Supervisor Form"):
        name = st.text_input("Supervisor Name", max_chars=100)
        workplace = st.selectbox(
            "Workplace",
            options=dbm.workplaces,
            format_func=lambda w: w.name,
        )
        if st.form_submit_button("Submit", use_container_width=True, type="primary"):
            if name and workplace:
                insert_supervisor(Supervisor(name=name, workplace_id=workplace.id))
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
                    dbm.insert(
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


def render_log_editor():
    row1 = st.columns([12, 58, 9, 9, 12], gap="xsmall", vertical_alignment="bottom")
    with row1[0]:
        st.subheader("Logs")
    with row1[-3]:
        view_date = st.date_input(
            "View Date",
            label_visibility="collapsed",
            key="view_scope_date",
        )
    with row1[-2]:
        view_scope = st.selectbox(
            "View Scope",
            label_visibility="collapsed",
            options=[v for v in ViewScope],
        )
    with row1[-1]:
        view_supervisor = st.selectbox(
            "View Supervisor",
            label_visibility="collapsed",
            options=[s for s in dbm.supervisors],
            format_func=lambda s: supervisor_label(s.id),
            index=None,
            placeholder="Select a supervisor",
        )
    filter_view(view_date, view_scope, view_supervisor)
    st.data_editor(
        st.session_state.log_df,
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
                default=0.0,
                step=0.01,
            ),
            "hours_a1": st.column_config.NumberColumn(
                label="🩺 Diagnosis & Treatment",
                help="Couples, families, and children",
                default=0.0,
                step=0.01,
            ),
            "hours_b": st.column_config.NumberColumn(
                label="💡 Non-Clinical Experience",
                default=0.0,
                step=0.01,
            ),
            "hours_b1": st.column_config.NumberColumn(
                label="🕵🏻‍♂️ Supervision, Individual, & Triadic",
                default=0.0,
                step=0.01,
            ),
            "hours_b2": st.column_config.NumberColumn(
                label="🔍 Supervision, Group",
                default=0.0,
                step=0.01,
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
        disabled=["_index", "id"],
        hide_index=True,
        key="log_editor",
        height=get_df_height(st.session_state.log_df),
    )

    row = st.columns([88, 12])
    with row[1]:
        st.button(
            "Add Log Entry",
            on_click=log_entry_dialog,
            use_container_width=True,
            icon="📝",
        )


def render_supervisor_editor():
    st.subheader("Supervisors")
    st.data_editor(
        st.session_state.sp_df,
        column_config={
            "name": st.column_config.TextColumn(
                label="🏷️ Name",
                required=True,
            ),
            "workplace_id": st.column_config.SelectboxColumn(
                label="🏢 Workplace",
                help="Select a workplace",
                options=(str(w.id) for w in dbm.workplaces),
                format_func=lambda id_: next(
                    w.name for w in dbm.workplaces if w.id == int(id_)
                ),
                required=True,
            ),
        },
        column_order=["name", "workplace_id"],
        num_rows="delete",
        disabled=["_index", "id"],
        hide_index=True,
        key="sp_editor",
        height=get_df_height(
            st.session_state.sp_df,
        ),
    )

    row = st.columns([88, 12])
    with row[1]:
        st.button(
            "Add Supervisor",
            on_click=add_supervisor_dialog,
            use_container_width=True,
            icon="👨‍💼",
        )


def render_workplace_editor():
    st.subheader("Workplaces")
    st.data_editor(
        st.session_state.wp_df,
        column_config={
            "name": st.column_config.TextColumn(label="🏷️ Name", required=True),
            "street": st.column_config.TextColumn(label="🛣️ Street", required=True),
            "city": st.column_config.TextColumn(label="🏙️ City", required=True),
            "state": st.column_config.TextColumn(label="🏛️ State", required=True),
            "zipcode": st.column_config.NumberColumn(
                label="📫 Zip code", required=True
            ),
        },
        column_order=["name", "street", "city", "state", "zipcode"],
        num_rows="delete",
        disabled=["_index", "id"],
        hide_index=True,
        key="wp_editor",
        height=get_df_height(
            st.session_state.wp_df,
        ),
    )

    row = st.columns([88, 12])
    with row[1]:
        st.button(
            "Add Workplace",
            on_click=add_workplace_dialog,
            use_container_width=True,
            icon="🏢",
        )


def render_associate_editor():
    st.subheader("Supervisors")


st.title("📝 Timesheet")
tabs = st.tabs(["Timesheet"])
with tabs[0]:
    row = st.columns([90, 10])
    with row[1]:
        if st.button("Save all", type="primary", use_container_width=True):
            try:
                dbm.save(Log, st.session_state.log_editor)
                dbm.save(Supervisor, st.session_state.sp_editor)
                dbm.save(Workplace, st.session_state.wp_editor)
                st.toast("Saved all tables", icon="✅", duration=1)
            except Exception as e:  # noqa: BLE001
                st.toast(f"{e}", icon="🚫")
    render_log_editor()
    st.space(size="xsmall")
    render_supervisor_editor()
    st.space(size="xsmall")
    render_workplace_editor()
with tabs[1]:
    pass
