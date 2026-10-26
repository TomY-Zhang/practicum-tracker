import streamlit as st


def main():
    st.set_page_config(layout="wide")
    pg = st.navigation([st.Page("pages/timesheet.py", title="Timesheet")])
    pg.run()


if __name__ == "__main__":
    main()
