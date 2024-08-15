import os
import streamlit as st
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
from collections import Counter
import re

# Load environment variables from .env file
load_dotenv()

# Set up the environment keys
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

# Company-specific details
COMPANY_NAME = "Axi"
COMPANY_DOMAIN = "axi.com"
COMPANY_ROLE = f'{COMPANY_NAME} Information Specialist'
COMPANY_GOAL = f'Provide accurate and detailed information about {COMPANY_NAME} products, services, and solutions available on lxme.in.'
COMPANY_BACKSTORY = (
    f'You are a knowledgeable specialist in {COMPANY_NAME}\'s offerings. '
    f'You provide detailed information about their products, services, '
    f'and solutions available on lxme.in, including any innovations and key features.'
)

# Initialize the SerperDevTool with company-specific search settings
class CompanySerperDevTool(SerperDevTool):
    def search(self, query):
        # Add a prefix to filter results to company-specific content
        company_query = f"site:{COMPANY_DOMAIN} {query}"
        results = super().search(company_query)
        # Filter results to include only company-specific content
        relevant_results = [result for result in results if COMPANY_DOMAIN in result.get('link', '')]
        return relevant_results

# Initialize the customized search tool
search_tool = CompanySerperDevTool()

# Company Information Agent setup
company_info_agent = Agent(
    role=COMPANY_ROLE,
    goal=COMPANY_GOAL,
    verbose=True,
    memory=True,
    backstory=COMPANY_BACKSTORY,
    tools=[search_tool]
)

# Out-of-Context Agent setup
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

# Centralized Task for determining user query context and responding appropriately
centralized_task = Task(
    description=(
        f'Determine if the user query is related to {COMPANY_NAME} and respond appropriately. '
        f'If the query is about {COMPANY_NAME}, provide a detailed and informative response. '
        f'If the query is out of context, respond politely indicating that only {COMPANY_NAME}-related information is provided. '
        f'User query: {{user_query}}'
    ),
    expected_output=f'A detailed response based on the context of the user query, focusing on {COMPANY_NAME} information.',
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

# Function to process user query and display result
def process_query(user_query):
    with st.spinner("Processing your input..."):
        result = centralized_crew.kickoff(inputs={'user_query': user_query})
        st.markdown(f"*Response:* {result}", unsafe_allow_html=True)
        # Generate dynamic relevant questions
        relevant_questions = generate_dynamic_questions(user_query)
        display_relevant_questions(relevant_questions)

# Function to generate dynamic relevant questions
def generate_dynamic_questions(user_query):
    # Example: Extract keywords and suggest related questions
    keywords = extract_keywords(user_query)
    relevant_questions = [f"What else can you tell me about {keyword} at {COMPANY_NAME}?" for keyword in keywords]
    return relevant_questions

# Function to extract keywords (simplistic approach)
def extract_keywords(query):
    words = re.findall(r'\w+', query)
    common_words = {'what', 'is', 'the', 'of', 'in', 'to', 'and', 'a', 'about'}
    keywords = [word.capitalize() for word in words if word.lower() not in common_words]
    # Return the most common keywords or terms
    return [word for word, count in Counter(keywords).most_common(3)]

# Function to display relevant questions
def display_relevant_questions(relevant_questions):
    st.markdown("### Relevant Questions:")
    for question in relevant_questions:
        if st.button(question):
            process_query(question)

# User input form
with st.form("query_form"):
    user_input = st.text_area(f"Enter your question about {COMPANY_NAME}:", height=150)
    submit_button = st.form_submit_button(label="Submit")

# Process form submission
if submit_button and user_input:
    process_query(user_input)

