import streamlit as st
from pathlib import Path
from sqlalchemy import text
import ast

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
    response = connection.query(f"SELECT * FROM Prompts WHERE name IS NOT 'Conversation control'")
    connection.session.close()
    return response

def get_tactics_prompt():
    connection = open_connection()
    response = connection.query(f"SELECT * FROM Prompts WHERE name IS 'UPDATE_TACTICS'")
    dictionary = ast.literal_eval(response)

    connection.session.close()
    return dictionary


def create_prompt(name, author, prompt, describe):
    with open_connection().session as session:
        query = text("INSERT INTO Prompts (name, author, prompt, describe) VALUES (:name, :author, :prompt, :describe)")
        session.execute(query, {"name": name, "author": author, "prompt": prompt, "describe": describe})
        session.commit()


def update_description():
    with open_connection().session as session:
        query = text("UPDATE Prompts SET describe = :describe WHERE name = :name")
        session.execute(query, {"describe": st.session_state.description_input, "name": st.session_state.selected_prompt})
        session.commit()


def update_prompt():
    with open_connection().session as session:
        query = text("UPDATE Prompts SET prompt = :prompt WHERE name = :name")
        session.execute(query, {"prompt": st.session_state.prompt_input, "name": st.session_state.selected_prompt})
        session.commit()


def get_control_prompt():
    connection = open_connection()
    response = connection.query("SELECT * FROM Prompts WHERE name IS 'Conversation control'")
    connection.session.close()
    return response


def update_control():
    with open_connection().session as session:
        query = text("UPDATE Prompts SET prompt = :prompt WHERE name = 'Conversation control'")
        session.execute(query, {"prompt": st.session_state.control_input})
        session.commit()


if __name__ == "__main__":
    init_db()
    fill_db()
    st.write("Database initialized")