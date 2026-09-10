import streamlit as st

if __name__ == "__main__":
    pg = st.navigation([st.Page("pages/home.py")])
    pg.run()
