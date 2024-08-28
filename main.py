import os
from dotenv import load_dotenv
import streamlit as st
from chatbot import render_chatbot


# Load environment variables from .env file
load_dotenv()

# Set up the environment keys
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")


# Define custom CSS
custom_css = """
<style>
/* Change the background color of the entire app */
body {
    background-color: #ffe6f2;
}

/* Change the color of the main title */
h1 {
    color: #bf1f61;
}

/* Style the chat messages */
.chat-message.user {
    background-color: #ffcccb;
    color: #bf1f61;
    border: 2px solid #bf1f61;
}

.chat-message.assistant {
    background-color: #ffffcc;
    color: #bf1f61;
    border: 2px solid #bf1f61;
}

/* Style the input box at the bottom */
.stTextInput > div {
    background-color: #ffcccb;
    border-radius: 5px;
    color: #bf1f61;
}

/* Style the buttons */
button {
    background-color: #bf1f61;
    color: #fff;
   
    border: none;
    border-radius: 5px;
}

.st-emotion-cache-1ghhuty{
background-color: #bf1f61;
}

.st-emotion-cache-bho8sy{
background-color: black;
}
/* Style the spinner */
.stSpinner > div {
    border-top-color: #bf1f61;
}

/* Style the download button */
.stDownloadButton {
    background-color: #bf1f61;
    color: #fff;
    border-radius: 5px;
}

.black-text {
    
    color: black;
    
}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

if "company_name" not in st.session_state:
    st.session_state.messages = []
    st.title("Instant demo chatbot for your own company")
    company_name = st.text_input("Company name")
    company_website = st.text_input("Company website")
    st.button("Create chatbot", on_click=lambda: st.session_state.update(company_name=company_name, company_website=company_website))
else:
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    render_chatbot(st.session_state["company_name"], st.session_state["company_website"])