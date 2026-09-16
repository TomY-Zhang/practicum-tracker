import streamlit as st


def main():
    st.set_page_config(layout="wide")
    pg = st.navigation([st.Page("pages/home.py", title="Home", icon="🏠")])
    pg.run()


if __name__ == "__main__":
    main()
