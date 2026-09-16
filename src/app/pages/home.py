import streamlit as st

from app.db import DatabaseManager
from app.db.models import Supervisor, Workplace

dbm = DatabaseManager()


def load_session() -> None:
    st.session_state.df = DatabaseManager.get_logs_dataframe()
    st.session_state.supervisors = DatabaseManager.get_supervisors()
    st.session_state.workplaces = DatabaseManager.get_workplaces()


@st.dialog("Add Supervisor")
def add_supervisor_dialog():
    with st.form("Add Supervisor Form"):
        name = st.text_input("Supervisor Name", max_chars=100)

        workplace_names: list[str] = list(st.session_state.workplaces.keys())
        workplace = st.selectbox("Workplace", workplace_names)

        if st.form_submit_button("Submit", use_container_width=True, type="primary"):
            if name and workplace:
                wp: Workplace = st.session_state.workplaces.get(workplace)
                if wp:
                    DatabaseManager.insert(Supervisor(name=name, workplace_id=wp.id))
                else:
                    st.toast(
                        f"Error: unable to determine ID for workplace '{workplace}'",
                        icon="🚫",
                    )
                st.toast(f"Added new supervisor '{name}'", icon="✅")
                st.rerun()
            else:
                st.toast("Please fill out all fields", icon="🚫")


@st.dialog("Add Workplace")
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


def render_page() -> None:
    st.title("Timesheet")

    st.data_editor(
        st.session_state.df,
        column_config={
            "date": st.column_config.DateColumn(
                label="Date",
                format="YYYY-MM-DD",
                required=True,
            ),
            "name": st.column_config.SelectboxColumn(
                label="Supervisor",
                help="Select supervisor",
                options=st.session_state.supervisors.keys(),
                required=True,
            ),
            "hours_a": st.column_config.NumberColumn(
                "Direct Counseling",
                help="Individuals, groups, couples, and families",
                default=0,
            ),
            "hours_a1": st.column_config.NumberColumn(
                label="Diagosis & Treatment",
                help="Couples, families, and children",
                default=0,
            ),
            "hours_b": st.column_config.NumberColumn(
                label="Non-Clinical Experience",
                default=0,
            ),
            "hours_b1": st.column_config.NumberColumn(
                label="Supervision, Individual, & Triadic",
                default=0,
            ),
            "hours_b2": st.column_config.NumberColumn(
                label="Supervision, Group",
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

    cols = st.columns([25, 2, 2, 1])

    with cols[-3]:
        if st.button("Add Supervisor", use_container_width=True):
            add_supervisor_dialog()

    with cols[-2]:
        if st.button("Add Workplace", use_container_width=True):
            add_workplace_dialog()

    with cols[-1]:
        if st.button("Save", use_container_width=True, type="primary"):
            dbm.save(st.session_state.editor)
            st.toast("Timesheet successfully saved", icon="✅")


load_session()
render_page()
