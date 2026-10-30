import streamlit as st

st.set_page_config(layout="wide")
pg = st.navigation([st.Page("timesheet.py", title="Timesheet")])  # ty: ignore[call-non-callable]
pg.run()
