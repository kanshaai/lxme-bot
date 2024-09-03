import streamlit as st
from dotenv import load_dotenv

from salesbot import salesbot
from storage import save_to_storage

# Load environment variables from .env file
load_dotenv()

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
    color: #9b51e0;
}

/* Style the chat messages */
.chat-message.user {
    background-color: #ffcccb;
    color: #9b51e0;
    border: 2px solid #9b51e0;
}

.chat-message.assistant {
    background-color: #ffffcc;
    color: #9b51e0;
    border: 2px solid #9b51e0;
}

/* Style the text input */
.stTextInput {
    position: fixed;
    bottom: 3rem;
}

/* Style the buttons */
button {
    background-color: #9b51e0;
    color: #fff;
   
    border: none;
    border-radius: 5px;
}

.st-emotion-cache-1ghhuty{
background-color: #9b51e0;
}

.st-emotion-cache-bho8sy{
background-color: #ff6900;
}
/* Style the spinner */
.stSpinner > div {
    border-top-color: #9b51e0;
}

/* Style the download button */
.stDownloadButton {
    background-color: #9b51e0;
    color: #fff;
    border-radius: 5px;
}

.st-emotion-cache-1dp5vir{
background-image: linear-gradient(90deg, rgb(155, 81, 224), rgb(155, 81, 224));
}

.black-text {
    color: black;
}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I help you today? Select an insurance category, or type your question below:"}]
if "page" not in st.session_state:
    st.session_state.page = "salesbot"
if "stored" not in st.session_state:
    st.session_state.stored = True
    save_to_storage()


salesbot()