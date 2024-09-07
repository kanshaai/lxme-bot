import json
import os
import streamlit as st
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
from pathlib import Path
from mail import send_logs_email

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


if "rephrase_prompt" not in st.session_state:
    st.session_state.rephrase_prompt = (
f'As context, you get the \n'
f'## Customer query: {{user_query}},\n'
f'## Original response: {{original_response}},\n'
f'## Conversation history so far: {{conversation}}\n'
f'Respond in JSON format with one keys: "answer"\n'
f'The "answer" key should \n'
f'Rephrase only the Original response given by a knowledge base agent: {{original_response}}\n'
f'The knowledge base agent is trained on the information available on a company called Jupiter,\n'
f"Into how the world's best customer support representative would respond\n"
f"In a way that validates the user's pain and consequence to the user, and makes clear they aim to resolve any issue as quickly as possible, and always stays solution-oriented,\n"
f'and never becomes helpless or apologetic or defends or justifies anything that has caused the user inconvenience, anger and pain\n'
f'and remains focused on providing concise reasons, and best recommended next action\n'
f'You can also use the knowledge base agent again if needed, but not too much, as in most cases you should have enough context to answer the question yourself.\n'
f'## Answer Guidelines\n'
f'Start by acknowledging what the user has mentioned they need to get done, and then their need, with a sentence that starts with "You" wherever possible instead of "I" to maintain user-centric-focus\n'
f"Focus on what can be done now, not what can't be done\n"
f'If you need to re-confirm a specific transaction, then pretend you have the entire user transaction history with the company, and make up some dummy transaction data to use to re-confirm these details with user\n'
f'Use your response to help shift a user from complaint-orientation to solution-orientation\n'
f'A concise, informative, actually helpful reply is best. \n'
f"In no situation, should you recommend that the user contact the company's customer support team directly, because you are already acting as the customer support team that the user has already contacted. Also do not recommend checking Jupiter Community Forum. Just focus on making progress happen wrt resolving user issue"
f'Every sentence should be sequenced exactly how a user in extreme pain would most care about receiving that information.\n'
f'Keep in mind the entire context of the conversation, not just the most recent messages. If you apologised before and the customer is still angry, there is no use in apologising again. Try a different tactic to reduce their anger.\n'
f'Empathise but Do not exaggerate on friendliness to the point that it seems insincere.\n'
f'Mention you will keep the user proactively updated on progress\n'
f'Focus on styling the response nicely. Use newlines and lists in markdown where appropriate. No other styling elements than lists and newlines should be in the response.\n'
f'Always ensure the response is in valid JSON format.'
    )


def rephraser_crew():
    centralized_task = Task(
        description=st.session_state.rephrase_prompt,
        expected_output='''A JSON object containing "answer" as key, with the response as the value.
The response should not contain any unescaped newline characters nor codeblock. The response should be able to pass JSON.loads() without any error.''',
        agent=Agent(
            role=f'{COMPANY_NAME} Customer Service Agent',
            goal= f'Provide a helpful and empathetic customer service response for chats about {COMPANY_NAME} products, services, and solutions',
            verbose=True,
            memory=True,
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


# Streamlit UI
st.markdown("""
    <h2 style="color:#ff796d; margin-left:5px;">
        Jupiter Customer Support + Rephraser
    </h2>
""", unsafe_allow_html=True)
st.write("<style>div.block-container{padding-top:2rem;}</style>", unsafe_allow_html=True)


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to save the chat history to a file
def save_chat_history(filename=f"{COMPANY_NAME}.txt"):
    with open(filename, "a", encoding="utf-8") as file:
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


def conversation_history(messages):
    # Make a string containing all messages in current history
    history = ''
    for message in messages:
        history += f"{message['role']}: {message['content']}\n"
    return history


# Function to process user query
def process_query(user_query):
    if user_query.lower() == "give me the logs 420":
        download_logs()
        return  # Exit the function to avoid processing the query further


    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    answer = ""  # Initialize the answer variable

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

    with st.chat_message("assistant"):
        with st.spinner("Rephrasing the answer..."):
            result2 = rephraser_crew().kickoff(inputs={'user_query': user_query, "original_response": answer, "conversation": conversation_history(st.session_state.messages)})
            try:
                # Remove potential markdown code block syntax
                cleaned_result = str(json.loads(result2.model_dump_json())['raw']).strip().replace('```json', '').replace('```', '')
                print(json.loads(result2.model_dump_json())['raw'])
                # Parse JSON response
                parsed_result = json.loads(cleaned_result)
                answer2 = parsed_result.get("answer", "")
                st.markdown(f"{answer2}")

            except json.JSONDecodeError as e:
                print(e)
                st.markdown(f"**Error parsing JSON:**\n{result2}")
                answer2 = "There was an error processing your request."

    st.session_state.messages.append({"role": "assistant", "content": answer2})

    # Save chat history to file
    save_chat_history()
    st.rerun()


def read_conversation(file_path):
    conversations = []
    with open(file_path, 'r') as file:
        message = {}
        append_content = False
        for line in file:
            line = line.strip()
            
            # Detect start of a new message
            if line.startswith('Role:'):
                if message:  # Add the previous message to conversations list
                    conversations.append(message)
                message = {"role": line.split(":")[1].strip(), "content": ""}
                append_content = False
            
            # Detect content start
            elif line.startswith('Content:'):
                message["content"] = line.split("Content:")[1].strip()
                append_content = True  # Start appending content lines
            
            # Append to the current content if no separator and in content mode
            elif append_content and not line.startswith('-------'):
                message["content"] += "\n" + line
            
            # If separator, end the current message
            elif line.startswith('------'):
                if message:  # Add the current message to conversations list
                    conversations.append(message)
                    message = {}
                append_content = False

        if message:  # Add the last message if any
            conversations.append(message)
    return conversations


def show_conversations(messages):
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def make_conversation(filepath):

    user = st.chat_input("User:")
    if user:
        st.session_state.messages.append({"role": "user", "content": user})
    assistant = st.chat_input("Assistant:")
    if assistant:
        st.session_state.messages.append({"role": "assistant", "content": assistant})
    if st.button("Rephrase"):
        u = conversation_history([[m for m in st.session_state.messages if m['role']=='user'][-1]])
        r = conversation_history([[m for m in st.session_state.messages if m['role']=='assistant'][-1]])
        c = conversation_history(st.session_state.messages)
        result = rephraser_crew().kickoff(inputs={
            'user_query': u,
            "original_response": r,
            "conversation": c
        })
        try:
            # Remove potential markdown code block syntax
            cleaned_result = str(json.loads(result.model_dump_json())['raw']).strip().replace('```json', '').replace('```', '')
            # Parse JSON response
            parsed_result = json.loads(cleaned_result[cleaned_result.find('{'):cleaned_result.rfind('}')+1])
            answer1 = parsed_result.get("answer", "")
            st.markdown(f"{answer1}")

        except json.JSONDecodeError as e:
            print(e)
            st.markdown(f"**Below response is not properly parsed:**\n{result}")
            answer1 = str(json.loads(result.model_dump_json())['raw'])

        st.session_state.messages.append({"role": "Rephraser", "content": answer1})
        # Function to save the chat history to a file
        with open(filepath, "a", encoding="utf-8") as file:
            for message in st.session_state.messages[-3:]:
                file.write(f"Role: {message['role']}\n")
                file.write(f"Content: {message['content']}\n")
                file.write("-" * 40 + "\n")

st.selectbox("Select a page", ["Chat", "Rephraser prompt", "Example 1", "Example 2", "Example 3", "Example 4"], key="page")

if st.session_state.page == "Chat":
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input at the bottom of the page
    user_input = st.chat_input(f"Enter your question about {COMPANY_NAME}:")

    if user_input:
        process_query(user_input)

if st.session_state.page == "Rephraser prompt":
    prompt = st.text_area("Current rephraser Prompt", value=st.session_state.rephrase_prompt, height=800)
    if st.button("Update Rephraser Prompt"):
        st.session_state.rephrase_prompt = prompt

if st.session_state.page == "Example 1":
    st.markdown("Example of an existing customer conversation, with the actual response from the agent, plus what the rephrased response would have been.")
    show_conversations(read_conversation('example.txt'))

if st.session_state.page == "Example 2":
    st.markdown("Example of an existing customer conversation, with the actual response from the agent, plus what the rephrased response would have been.")
    show_conversations(read_conversation('example3.txt'))

if st.session_state.page == "Example 3":
    st.markdown("Example of an existing customer conversation, with the actual response from the agent, plus what the rephrased response would have been.")

if st.session_state.page == "Example 4":
    st.markdown("Examples of made up customer queries, our own chatbot answer, and the rephrased response.")
    make_conversation("example2.txt")