import pandas as pd
import streamlit as st

# Setup
structure = {
    "ID": pd.Series(dtype="int64"),
    "Date": pd.Series(dtype="datetime64[us]"),
    "A Hours": pd.Series(dtype="int8"),
    "A1 Hours": pd.Series(dtype="int8"),
    "B Hours": pd.Series(dtype="int8"),
    "B1 Hours": pd.Series(dtype="int8"),
    "B2 Hours": pd.Series(dtype="int8"),
    "C Hours": pd.Series(dtype="int8"),
    "Supervisor": pd.Series(dtype="string"),
    "Workplace": pd.Series(dtype="string"),
}


def handle_editor_change():
    changes = st.session_state.editor

    if changes["deleted_rows"]:
        st.session_state.df = st.session_state.df.drop(changes["deleted_rows"])

    for row_idx, updates in changes["edited_rows"].items():
        for col, val in updates.items():
            st.session_state.df.at[row_idx, col] = val


def handle_save():
    pass


# Session state config
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(structure)

if not "status" in st.session_state:
    st.session_state.status = None


# Render page
st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")
st.title("Timesheet")

if st.session_state.status:
    status, msg = st.session_state.status
    if status == "success":
        st.success(msg)
    elif status == "error":
        st.error(msg)

col1, col2, _ = st.columns([1, 1, 12])
with col1:
    st.button("Add Supervisor", use_container_width=True)

with col2:
    st.button("Add Workplace", use_container_width=True)

st.data_editor(
    st.session_state.df,
    column_config={
        "Date": st.column_config.DateColumn(
            "Date",
            format="YYYY-MM-DD",  # Formats display to show date only
        )
    },
    on_change=handle_editor_change,
    disabled=["ID", "_index"],
    key="editor",
    column_order=[
        "Date",
        "A Hours",
        "A1 Hours",
        "B Hours",
        "B1 Hours",
        "B2 Hours",
        "C Hours",
    ],  # hide ID column but preserve its value
    num_rows="dynamic",
    hide_index=True,
    height="auto",
)

if st.button("Save"):
    st.session_state.status = ("success", "Timesheet successfully saved")
