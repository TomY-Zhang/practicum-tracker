import pandas as pd
import streamlit as st
from sqlalchemy import orm, select

from app.db import Session, engine
from app.db.models import Log, Supervisor, Workplace

# Setup
column_map = {
    "id": "ID",
    "date": "Date",
    "hours_a": "A Hours",
    "hours_a1": "A1 Hours",
    "hours_b": "B Hours",
    "hours_b1": "B1 Hours",
    "hours_b2": "B2 Hours",
    "name": "Supervisor",
}


def load_df() -> None:
    stmt = select(Log, Supervisor).join(
        Supervisor,
        Log.supervisor_id == Supervisor.id,
    )
    df = pd.read_sql_query(stmt, con=engine).rename(columns=column_map)
    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d")
    df.drop(
        columns=["supervisor_id", "id_1", "workplace_id", "hours_c"],
        inplace=True,
    )
    st.session_state.df = df


def load_supervisor_map(session: orm.Session | None = None) -> None:
    if session:
        supervisors = session.query(Supervisor).all()
    else:
        with Session() as s:
            supervisors = s.query(Supervisor).all()
    st.session_state.supervisor_ids = {s.name: s.id for s in supervisors}


def load_workplace_map(session: orm.Session | None = None) -> None:
    if session:
        workplaces = session.query(Workplace).all()
    else:
        with Session() as s:
            workplaces = s.query(Workplace).all()
    st.session_state.workplace_ids = {w.name: w.id for w in workplaces}


@st.dialog("Add Supervisor")
def add_supervisor_dialog():
    with st.form("Add Supervisor Form"):
        name = st.text_input("Name")

        workplace_names: list[str] = list(st.session_state.workplace_ids.keys())
        workplace = st.selectbox("Workplace", workplace_names)

        if st.form_submit_button("Submit"):
            if name and workplace:
                workplace_id = st.session_state.workplace_ids.get(workplace)
                if workplace_id:
                    with Session() as session:
                        session.add(Supervisor(name=name, workplace_id=workplace_id))
                        session.commit()
                        load_supervisor_map(session)
                else:
                    st.toast(
                        f"Error: unable to determine ID for workplace '{workplace}'",
                        icon="🚫",
                    )
                st.toast(f"Added new supervisor '{name}'", icon="✅")
                st.rerun()
            else:
                st.toast("Please fill out all fields", icon="🚫")


def validate_date() -> None:
    pass


def save_timesheet() -> None:
    pass


# Session state config
load_df()
load_supervisor_map()
load_workplace_map()


# Render page
st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")
st.title("Timesheet")

st.data_editor(
    st.session_state.df,
    column_config={
        "Date": st.column_config.DateColumn(
            "Date",
            format="YYYY-MM-DD",  # Formats display to show date only
            required=True,
        ),
        "Supervisor": st.column_config.SelectboxColumn(
            "Supervisor",
            help="Select supervisor",
            options=st.session_state.supervisor_ids.keys(),
            required=True,
        ),
    },
    column_order=[
        "Date",
        "A Hours",
        "A1 Hours",
        "B Hours",
        "B1 Hours",
        "B2 Hours",
        "C Hours",
        "Supervisor",
    ],
    disabled=["ID", "_index"],
    key="editor",
    num_rows="dynamic",
    hide_index=False,
    height="auto",
)

_, col1, col2 = st.columns([30, 2, 1])

with col1:
    if st.button("Add Supervisor", use_container_width=True):
        add_supervisor_dialog()

with col2:
    if st.button("Save", use_container_width=True):
        save_timesheet()
        st.toast("Timesheet successfully saved", icon="✅")
