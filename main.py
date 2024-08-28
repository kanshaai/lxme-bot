import requests
import streamlit as st
from chatbot import render_chatbot

st.set_page_config(layout="wide")

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

def start_chat():
    company_name = st.session_state.name_input
    company_website = st.session_state.website_input
    if len(company_name.strip()) == 0 or len(company_website.strip()) == 0:
        st.error("Please enter a company name and website.")
        return
    try:
        response = requests.head(company_website, allow_redirects=True)
        valid_url = response.status_code == 200
    except requests.exceptions.RequestException:
        valid_url = False
    if not valid_url:
        st.error("Please provide a valid company website. This one cannot be accessed.")
        return
    st.session_state.chat_started = True
    st.session_state.company_name = company_name
    st.session_state.company_website = company_website
    

if "chat_started" not in st.session_state:
    st.session_state.messages = []
    
    st.title("Instant demo chatbot for your own company")
    left, _, _ = st.columns(3)
    with left:
        hide_enter = """
        <style>
        div[data-testid="InputInstructions"] > span:nth-child(1) {
            visibility: hidden;
        }
        </style>
        """
        st.markdown(hide_enter, unsafe_allow_html=True)
        company_name = st.text_input("Company name", key="name_input")
        company_website = st.text_input("Company website", key="website_input", help="Provide a valid url to your companies website to retrieve written information, such as FAQ or documentation.")
    st.button("Create chatbot", on_click=lambda: start_chat())
else:
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    render_chatbot(st.session_state.company_name, st.session_state.company_website)