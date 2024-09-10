import json
import os
import streamlit as st
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
from pathlib import Path
import db

# Load environment variables from .env file
load_dotenv()

# Set up the environment keys
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

# Company-specific details
COMPANY_NAME = "Jupiter Money"
COMPANY_DOMAIN = "jupiter.money/"


# Initialize the SerperDevTool with company-specific search settings
class CompanySerperDevTool(SerperDevTool):
    def search(self, query):
        company_query = f"site:{COMPANY_DOMAIN} {query}"
        results = super().search(company_query)
        relevant_results = [result for result in results if COMPANY_DOMAIN in result.get('link', '')]
        return relevant_results

search_tool = CompanySerperDevTool()


def information_crew():

    company_info_agent = Agent(
        role=f'{COMPANY_NAME} Information Specialist',
        goal=f'Provide accurate and detailed information about {COMPANY_NAME} products, services, and solutions available on {COMPANY_DOMAIN}.',
        verbose=True,
        memory=True,
        model_name="gpt-4o-mini",
        backstory=f'You are a knowledgeable specialist in {COMPANY_NAME}\'s offerings. '
        f'You provide detailed information about their products, services, '
        f'and solutions available on {COMPANY_DOMAIN}, including any innovations and key features.',
        tools=[search_tool]
    )

    out_of_context_agent = Agent(
        role='Context Checker',
        goal=f'Determine if a question is relevant to {COMPANY_NAME} and politely decline if not.',
        verbose=True,
        memory=True,
        model_name="gpt-4o-mini",
        backstory=(
            f'You are responsible for determining if a question is relevant to {COMPANY_NAME}. '
            f'If the question is not related, you respond politely indicating that the question is out of context and '
            f'that only {COMPANY_NAME}-related information is provided.'
        )
    )

    centralized_task = Task(
        description=(
            f'Determine if the {{user_query}} is related to {COMPANY_NAME} and respond appropriately.'
            f'First ask the Context Checker if the query is related to the company or not.'
            f'Then ask the {COMPANY_NAME} Information Specialist to provide detailed information relevant to the user query.'
            f'If the query is about {COMPANY_NAME}, provide a detailed and informative response.'
            f'Respond in JSON format with one key: "answer", which should contain the response.'
            f'Ensure the response is in valid JSON format.'
        ),
        expected_output='''A JSON object containing "answer" as key, with the response as the value.
The response should not contain any unescaped newline characters nor codeblock. The response should be able to pass JSON.loads() without any error.''',
        agent=Agent(
            role=f'{COMPANY_NAME} Information Bot',
            goal=f'Provide comprehensive information about {COMPANY_NAME} and its offerings.',
            verbose=True,
            memory=True,
            model_name="gpt-4o-mini",
            backstory=(
                f'You are an intelligent bot specializing in {COMPANY_NAME} information. You provide detailed responses '
                f'about {COMPANY_NAME}\'s trading platforms, financial instruments, account types, and market analysis tools. '
                f'You only respond to queries related to {COMPANY_NAME}.'
            ),
            allow_delegation=True
        )
    )

    crew = Crew(
        agents=[company_info_agent, out_of_context_agent],
        tasks=[centralized_task],
        process=Process.sequential
    )
    return crew


def conversation_control_crew(original_response):
    description = db.get_control_prompt()["prompt"].iloc[0]
    description = description.replace("{{conversation}}", original_response)
    centralized_task = Task(
        description=description,
        expected_output='''A JSON object containing "prompt" as key, with the prompt description as the value.''',
        agent=Agent(
            role='Conversation Controller',
            goal='Control the flow of the conversation and provide guidance to the agents.',
            verbose=True,
            memory=True,
            model_name="gpt-4o-mini",
            backstory=(
                'You are responsible for managing the conversation flow between agents. '
                'You provide guidance to the agents and ensure that the conversation stays on track.'
            )
        )
    )

    crew = Crew(
        tasks=[centralized_task],
        process=Process.sequential
    )
    return crew


def rephraser_crew(prompt):
    centralized_task = Task(
        description=prompt,
        expected_output='''A JSON object containing "answer" as key, with the response as the value.
The response should not contain any unescaped newline characters nor codeblock. The response should be able to pass JSON.loads() without any error.''',
        agent=Agent(
            role=f'{COMPANY_NAME} Customer Service Agent',
            goal= f'Provide a helpful and empathetic customer service response for chats about {COMPANY_NAME} products, services, and solutions',
            verbose=True,
            memory=True,
            model_name="gpt-4o-mini",
            backstory=(
                f'You are a helpful assistant working with clients of {COMPANY_NAME}.'
                f'You use detailed information about their products, services, and solutions available on {COMPANY_DOMAIN}'
                f'and communicate this information to the customer in a way that is friendly, customer centric, and aims to resolve the issue as quickly as possible.'
            ),
            allow_delegation=True
        )
    )

    crew = Crew(
        tasks=[centralized_task],
        process=Process.sequential
    )
    return crew


# Function to save the chat history to a file
def save_chat_history(filename=f"{COMPANY_NAME}.txt"):
    with open(filename, "a", encoding="utf-8") as file:
        for message in st.session_state.messages:
            file.write(f"Role: {message['role']}\n")
            file.write(f"Content: {message['content']}\n")
            file.write("-" * 40 + "\n")

# Function to handle log downloads
def download_logs():
    log_file = f"Jupter Money.txt"
    if Path(log_file).exists():
        # Prompt the user to download the file
        st.download_button(
            label="Download Conversation",
            data=open(log_file, "rb").read(),
            file_name=log_file,
            mime="text/plain"
        )
    else:
        st.write("No logs found.")


def download_rephraser():
    log_file = f"rephraser.db"
    if Path(log_file).exists():
        # Prompt the user to download the file
        st.download_button(
            label="Download Prompts",
            data=open(log_file, "rb").read(),
            file_name=log_file,
            mime="application/octet-stream"
        )
    else:
        st.write("No logs found.")


def conversation_history(messages):
    # Make a string containing all messages in current history
    history = ''
    for message in messages:
        if message['role'] == 'Control':
            continue
        history += f"{message['role']}: {message['content']}\n"
    return history


# Function to process user query
def process_query(user_query):
    if user_query.lower() == "give me the logs 420":
        download_logs()
        return  # Exit the function to avoid processing the query further
    
    if user_query.lower() == "give me the prompts 420":
        download_logs()
        return  # Exit the function to avoid processing the query further


    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    with st.chat_message("assistant"):
        with st.spinner("Initial answer for your input..."):
            result1 = information_crew().kickoff(inputs={'user_query': user_query})
            try:
                # Remove potential markdown code block syntax
                cleaned_result = str(json.loads(result1.model_dump_json())['raw']).strip().replace('```json', '').replace('```', '')
                print(json.loads(result1.model_dump_json())['raw'])
                # Parse JSON response
                parsed_result = json.loads(cleaned_result)
                answer1 = parsed_result.get("answer", "")
                st.markdown(f"{answer1}")

            except json.JSONDecodeError as e:
                print(e)
                st.markdown(f"**Error parsing JSON:**\n{result1}")
                answer1 = "There was an error processing your request."

    st.session_state.messages.append({"role": "assistant", "content": answer1})

    with st.spinner("Guiding the conversation..."):
        result2 = conversation_control_crew().kickoff()
        
        try:
            # Remove potential markdown code block syntax
            cleaned_result = str(json.loads(result2.model_dump_json())['raw']).strip().replace('```json', '').replace('```', '')
            print(json.loads(result2.model_dump_json())['raw'])
            # Parse JSON response
            parsed_result = json.loads(cleaned_result)
            answer2 = parsed_result.get("prompt", "")
            st.markdown(f"{answer2}")

        except json.JSONDecodeError as e:
            print(e)
            #st.markdown(f"**Error parsing JSON:**\n{result2}")
            answer2 = str(json.loads(result2.model_dump_json())['raw']).strip().replace('```json', '').replace('```', '')
    st.session_state.messages.append({"role": "Control", "content": answer2})

    with st.chat_message("assistant"):
        with st.spinner("Rephrasing the answer..."):
            prompts = db.get_prompts()
            
            try:
                prompt = prompts[prompts["describe"]==answer2]["prompt"].iloc[0]
            except:
                st.error(f"Prompt description '{answer2}' not found by conversation control. Please refine description and conversation control prompt")
                return
            st.session_state.chat_prompt = prompt.replace("{{user_query}}", user_query).replace("{{original_response}}", answer1).replace("{{conversation}}", conversation_history(st.session_state.messages))
            result3 = rephraser_crew().kickoff()
            try:
                # Remove potential markdown code block syntax
                cleaned_result = str(json.loads(result3.model_dump_json())['raw']).strip().replace('```json', '').replace('```', '')
                print(json.loads(result2.model_dump_json())['raw'])
                # Parse JSON response
                parsed_result = json.loads(cleaned_result)
                answer3 = parsed_result.get("answer", "")
                st.markdown(f"{answer3}")

            except json.JSONDecodeError as e:
                print(e)
                #st.markdown(f"**Error parsing JSON:**\n{result2}")
                answer3 = str(json.loads(result3.model_dump_json())['raw']).strip().replace('```json', '').replace('```', '')

    st.session_state.messages.append({"role": "assistant", "content": answer3})

    # Save chat history to file
    save_chat_history()
    st.rerun()


def render_chat():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    #prompts = db.get_prompts()
    #st.selectbox("Prompt for chat", prompts["name"], key="selected_chat_prompt")
    #st.session_state["chat_prompt"] = prompts[prompts["name"]==st.session_state.selected_chat_prompt]["prompt"].iloc[0]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input at the bottom of the page
    user_input = st.chat_input(f"Enter your question about Jupiter:")

    if user_input:
        process_query(user_input)