import streamlit as st
import db
from chat import render_chat
from chat_with_tactics import render_chat_tactics

from mvp_with_tactics import render_chat_mvp


#st.selectbox("Page", ["Prompts", "Chat", "Example 1", "Example 2", "Example 3"], key="page")
st.selectbox("Page", ["Prompts", "Control prompt", "Chat", "Chat with tactics","MVP with tactics"], key="page")
st.cache_data.clear()

if "create_prompt" not in st.session_state:
    st.session_state.create_prompt = False

def create_prompt():
    name = st.session_state.name_input
    author = st.session_state.author_input
    prompt = st.session_state.prompt_input
    if name.strip() == "" or author.strip() == "" or prompt.strip() == "":
        st.error("Please fill in all fields.")
        return
    st.session_state.create_prompt = False
    db.create_prompt(name, author, prompt, st.session_state.description_input)
    st.session_state.selected_prompt = name


def render_prompt():
    st.write("Select an existing prompt or create a new one.")
    prompts = db.get_prompts()
    left, right = st.columns(2)
    with left:
        st.selectbox("Select prompt", prompts["name"], key="selected_prompt", on_change=lambda: st.session_state.update(create_prompt=False))
    with right:
        st.button(":heavy_plus_sign: Create prompt", on_click=lambda: st.session_state.update(create_prompt=True))
    st.markdown("---")
    if st.session_state.create_prompt:
        left, right = st.columns(2)
        with left:
            st.text_input("Prompt name", key="name_input")
        with right:
            st.text_input("Author", key="author_input")
        prompt = prompts[prompts["name"]==st.session_state.selected_prompt]
        st.text_area("Prompt", key="prompt_input", value=prompt["prompt"].iloc[0], height=600)
        st.text_area("Description", key="description_input", height=100)
        st.button("Create", on_click=lambda: create_prompt())
    elif "selected_prompt" in st.session_state:
        prompt = prompts[prompts["name"]==st.session_state.selected_prompt]
        st.write(f"**Name:** {prompt['name'].iloc[0]}")
        st.write(f"**Author:** {prompt['author'].iloc[0]}")
        st.write(f"**Created at:** {prompt['created_at'].iloc[0]}")
        st.write("### Prompt")
        st.write(prompt["prompt"].iloc[0])
        st.text_area("**Description**", prompt["describe"].iloc[0], height=100, key="description_input")
        st.button("Save Description", on_click=lambda: db.update_description())


def render_control_prompt():
    st.write("Control prompt")
    prompt = db.get_control_prompt()
    st.write("### Prompt")
    st.text_area("Prompt", key="control_input", value=prompt["prompt"].iloc[0], height=600)
    st.button("Update", on_click=lambda: db.update_control())
    

if st.session_state.page == "Prompts":
    render_prompt()

if st.session_state.page == "Chat":
    render_chat()

if st.session_state.page == "Control prompt":
    render_control_prompt()


if st.session_state.page == "Chat with tactics":
    render_chat_tactics()



if st.session_state.page == "MVP with tactics":
    render_chat_mvp()