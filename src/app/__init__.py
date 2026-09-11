import streamlit as st


def main():
    pg = st.navigation([st.Page("pages/home.py")])
    pg.run()


if __name__ == "__main__":
    main()
