import streamlit as st
import db

st.selectbox("Page", ["Prompts", "Chat", "Example 1", "Example 2", "Example 3"], key="page")


def render_prompt():
    st.write("Select an existing prompt or create a new one.")
    prompts = db.get_prompts()
    left, right = st.columns(2)
    with left:
        st.selectbox("Select prompt", prompts["name"], key="selected_prompt")
    with right:
        st.button(":heavy_plus_sign: Create prompt", key="create_prompt")
    if st.session_state.create_prompt:
        left, right = st.columns(2)
        with left:
            st.text_input("Prompt name", key="name_input")
        with right:
            st.text_input("Author", key="author_input")
        st.text_area("Prompt", key="prompt_input", height=600)
        st.text_area("Description (optional)", key="description_input", height=200)
        st.button("Create", key="create")
    elif "selected_prompt" in st.session_state:
        prompt = prompts[prompts["name"]==st.session_state.selected_prompt]
        st.write(prompt["name"].iloc[0])
        st.write(prompt["author"].iloc[0])
        st.write(prompt["prompt"].iloc[0])
    

if st.session_state.page == "Prompts":
    render_prompt()

if st.session_state.page == "Chat":
    st.write("Chat")

if st.session_state.page == "Example 1":
    st.write("Example 1")

if st.session_state.page == "Example 2":
    st.write("Example 2")

if st.session_state.page == "Example 3":
    st.write("Example 3")