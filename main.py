import json
import os
import streamlit as st
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
from collections import Counter
import re
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Set up the environment keys
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

# Company-specific details
COMPANY_NAME = "ANZ Banking"
COMPANY_DOMAIN = "anz.com.au"
COMPANY_ROLE = f'{COMPANY_NAME} Information Specialist'
COMPANY_GOAL = f'Provide accurate and detailed information about {COMPANY_NAME} products, services, and solutions available on {COMPANY_DOMAIN}.'
COMPANY_BACKSTORY = (
    f'You are a knowledgeable specialist in {COMPANY_NAME}\'s offerings. '
    f'You provide detailed information about their products, services, '
    f'and solutions available on {COMPANY_DOMAIN}, including any innovations and key features.'
)


# Initialize the SerperDevTool with company-specific search settings
class CompanySerperDevTool(SerperDevTool):
    def search(self, query):
        company_query = f"site:{COMPANY_DOMAIN} {query}"
        results = super().search(company_query)
        relevant_results = [result for result in results if COMPANY_DOMAIN in result.get('link', '')]
        return relevant_results

search_tool = CompanySerperDevTool()

# Agent setups
company_info_agent = Agent(
    role=COMPANY_ROLE,
    goal=COMPANY_GOAL,
    verbose=True,
    memory=True,
    backstory=COMPANY_BACKSTORY,
    tools=[search_tool]
)

out_of_context_agent = Agent(
    role='Context Checker',
    goal=f'Determine if a question is relevant to {COMPANY_NAME} and politely decline if not.',
    verbose=True,
    memory=True,
    backstory=(
        f'You are responsible for determining if a question is relevant to {COMPANY_NAME}. '
        f'If the question is not related, you respond politely indicating that the question is out of context and '
        f'that only {COMPANY_NAME}-related information is provided.'
    )
)

# Centralized Task
centralized_task = Task(
    description=(
        f'Determine if the {{user_query}} is related to {COMPANY_NAME} and respond appropriately. '
        f'If the query is about {COMPANY_NAME}, provide a detailed and informative response. '
        f'Respond in JSON format with two keys: "answer" and "questions". '
        f'The "answer" key should contain the response, and the "questions" key should be an array of three follow-up questions '
        f'that are relevant to {COMPANY_NAME}.'
        f'Ensure the response is in valid JSON format.'
    ),
    expected_output='A JSON object containing "answer" and "questions".',
    agent=Agent(
        role=f'{COMPANY_NAME} Information Bot',
        goal=f'Provide comprehensive information about {COMPANY_NAME} and its offerings.',
        verbose=True,
        memory=True,
        backstory=(
            f'You are an intelligent bot specializing in {COMPANY_NAME} information. You provide detailed responses '
            f'about {COMPANY_NAME}\'s trading platforms, financial instruments, account types, and market analysis tools. '
            f'You only respond to queries related to {COMPANY_NAME}.'
        ),
        tools=[search_tool],
        allow_delegation=True
    )
)

# Centralized Crew setup
centralized_crew = Crew(
    agents=[company_info_agent, out_of_context_agent],
    tasks=[centralized_task],
    process=Process.sequential
)

# Streamlit UI
st.title(f"{COMPANY_NAME} Information Assistant")
st.write("<style>div.block-container{padding-top:2rem;}</style>", unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Function to save the chat history to a file
def save_chat_history(filename=f"{COMPANY_NAME}.txt"):
    with open(filename, "a") as file:
        for message in st.session_state.messages:
            file.write(f"Role: {message['role']}\n")
            file.write(f"Content: {message['content']}\n")
            file.write("-" * 40 + "\n")

# Function to handle log downloads
def download_logs():
    log_file = f"{COMPANY_NAME}.txt"
    if Path(log_file).exists():
        # Prompt the user to download the file
        st.download_button(
            label="Download Logs",
            data=open(log_file, "rb").read(),
            file_name=log_file,
            mime="text/plain"
        )
    else:
        st.write("No logs found.")


def process_follow_up(question):
    st.session_state.messages.append({"role": "user", "content": question})
    process_query(question)  # Reprocess the follow-up question

def process_query(user_query):
    if user_query.lower() == "give me the logs 420":
        download_logs()
        return  # Exit the function to avoid processing the query further

    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    with st.chat_message("assistant"):
        with st.spinner("Processing your input..."):
            result = centralized_crew.kickoff(inputs={'user_query': user_query})
            try:
                # Remove potential markdown code block syntax
                cleaned_result = str(result).strip('```json').strip()
                # Parse JSON response
                parsed_result = json.loads(cleaned_result)
                answer = parsed_result.get("answer", "")
                questions = parsed_result.get("questions", [])
                st.markdown(f"{answer}")
                
                # Use session state to manage follow-up question state
                if "follow_up" not in st.session_state:
                    st.session_state.follow_up = None

                # Create buttons for follow-up questions
                for question in questions:
                    if st.button(question):
                        st.session_state.follow_up = question
                        process_follow_up(question)  # Process the selected follow-up question

            except json.JSONDecodeError:
                st.markdown(f"**Error parsing JSON:**\n{result}")

    st.session_state.messages.append({"role": "assistant", "content": result})

    # Save chat history to file
    save_chat_history()

# Chat input at the bottom of the page
user_input = st.chat_input(f"Enter your question about {COMPANY_NAME}:")

if user_input:
    process_query(user_input)
