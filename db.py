import streamlit as st
from pathlib import Path
from sqlalchemy import text

def open_connection():
    return st.connection("rephraser_db", type="sql", url="sqlite:///rephraser.db")


def init_db():
    with open_connection().session as session:
        session.execute(text(Path("sql/create_prompts.sql").read_text()))
        session.execute(text(Path("sql/create_conversation.sql").read_text()))
        session.execute(text(Path("sql/create_messages.sql").read_text()))
        session.execute(text(Path("sql/create_rephrased.sql").read_text()))
        session.commit()


def fill_db():
    with open_connection().session as session:
        session.execute(text(Path("sql/fill_prompts.sql").read_text()))
        session.commit()


def get_prompts():
    connection = open_connection()
    response = connection.query(f"SELECT * FROM Prompts")
    connection.session.close()
    return response


if __name__ == "__main__":
    init_db()
    fill_db()
    st.write("Database initialized")