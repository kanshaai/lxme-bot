import json
import os
from pathlib import Path
from flask import Flask, request, render_template, jsonify, send_file
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
from mail import send_logs_email

# Load environment variables from .env file
load_dotenv()

# Set up the environment keys
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

# Company-specific details
COMPANY_NAME = "Lxme"
COMPANY_DOMAIN = "lxme.in"
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
        # Search the company website
        company_query = f"site:{COMPANY_DOMAIN} {query}"
        results = super().search(company_query)
        relevant_results = [result for result in results if COMPANY_DOMAIN in result.get('link', '')]
        return results

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
    expected_output='A JSON object containing "answer", and "questions" without any unescaped newline characters and without any codeblock.',
    agent=Agent(
        role=f'{COMPANY_NAME} Information Bot',
        goal=f'Provide comprehensive information about {COMPANY_NAME} and its offerings.',
        verbose=True,
        memory=True,
        backstory=(
            f'You are an intelligent bot specializing in {COMPANY_NAME} information. You provide detailed responses '
            f'about {COMPANY_NAME}\'s products, services, and innovations.'
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

# Initialize Flask app
app = Flask(__name__)

# Helper function to check links
def check_links(links, user_query):
    web_links = []
    youtube_links = []
    for link in links:
        if COMPANY_DOMAIN in link:
            web_links.append(link)
        if "youtube.com" in link and "watch" in link:
            youtube_links.append(link)
    return web_links, youtube_links

# Function to save the chat history to a file
def save_chat_history(filename=f"{COMPANY_NAME}.txt", chat_history=None):
    with open(filename, "a", encoding="utf-8") as file:
        for message in chat_history:
            file.write(f"Role: {message['role']}\n")
            file.write(f"Content: {message['content']}\n")
            file.write("-" * 40 + "\n")

# Route for the chat interface
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_query = request.form["user_input"]
        chat_history = []

        if user_query.lower() == "give me the logs 420":
            return send_file(f"{COMPANY_NAME}.txt", as_attachment=True)

        if user_query.lower() == "email me the logs 420":
            email = request.form.get("email")
            if email:
                success, message = send_logs_email(email, COMPANY_NAME)
                return jsonify({"success": success, "message": message})

        # Process the query using Crew
        result = centralized_crew.kickoff(inputs={'user_query': user_query})
        try:
            # Parse the JSON response
            cleaned_result = str(json.loads(result.model_dump_json())['raw']).strip().replace('```json', '').replace('```', '')
            parsed_result = json.loads(cleaned_result)
            answer = parsed_result.get("answer", "")
            links = parsed_result.get("links", "")
            web_links, youtube_links = check_links(links, user_query)

            if web_links or youtube_links:
                answer += "\n\nFor your reference:\n"
                if youtube_links:
                    answer += "\nYouTube references:\n" + "\n".join(youtube_links)
                if web_links:
                    answer += "\nWeb references:\n" + "\n".join(web_links)

            questions = parsed_result.get("questions", [])
            chat_history.append({"role": "assistant", "content": answer})

            save_chat_history(chat_history=chat_history)
            print("Answer:", answer)  # Debugging print
            print("Questions:", questions)  # Debugging print
            return jsonify({"answer": answer, "questions": questions})

        except json.JSONDecodeError as e:
            print("JSON Decode Error:", e)  # Debugging print
            return jsonify({"error": "Error parsing JSON response."})

        except Exception as e:
            print("An unexpected error occurred:", e)  # Debugging print
            return jsonify({"error": "An unexpected error occurred."})

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
