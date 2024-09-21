from flask import Flask, render_template_string, request, jsonify
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up the environment keys
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

# Company-specific details
COMPANY_NAME = "Axi"
COMPANY_DOMAIN = "axi.com"
COMPANY_ROLE = f'{COMPANY_NAME} Information Specialist'
COMPANY_GOAL = f'Provide accurate and detailed information about {COMPANY_NAME} products, services, and solutions available on {COMPANY_DOMAIN}'
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

app = Flask(__name__)

@app.route('/')
def index():
    # HTML content including your script
    html_content = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Axi Support Bot</title>
    </head>
    <body>
        <h1>Welcome to the Axi Support Bot</h1>
        <!-- Your script goes here -->
        <script id="ze-snippet" src="https://static.zdassets.com/ekr/snippet.js?key=d0572b05-fe1b-463d-8726-ac1b7d1bb074"></script>
    </body>
    </html>
    '''
    return render_template_string(html_content)

@app.route('/query', methods=['POST'])
def query():
    user_query = request.json.get('query')
    if not user_query:
        return jsonify({'error': 'No query provided'}), 400

    # Process the query using the centralized crew
    result = centralized_crew.kickoff(inputs={'user_query': user_query})
    print(result)
    # Return the result as JSON
    return jsonify({'response': str(result)})

if __name__ == '__main__':
    app.run(debug=True)
