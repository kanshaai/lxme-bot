from crewai import Agent, Task, Crew, Process
import json
import pandas as pd

import warnings


COMPANY_NAME = "Jupiter Money"
COMPANY_DOMAIN = "jupiter.money/"


def conversation_control_crew(conversation, prompt):
    description = prompt.replace("{{conversation}}" , conversation)
    centralized_task = Task(
        description=description,
        expected_output='''A JSON object containing "prompt" as key, with the prompt description as the value.''',
        agent=Agent(
            role='Conversation Controller',
            goal='Control the flow of the conversation and provide guidance to the agents.',
            verbose=False,
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


def rephraser_crew(chat_prompt):
    centralized_task = Task(
        description=chat_prompt,
        expected_output='''A JSON object containing "answer" as key, with the response as the value.
The response should not contain any unescaped newline characters nor codeblock. The response should be able to pass JSON.loads() without any error.''',
        agent=Agent(
            role=f'{COMPANY_NAME} Customer Service Agent',
            goal= f'Provide a helpful and empathetic customer service response for chats about {COMPANY_NAME} products, services, and solutions',
            verbose=False,
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



# Function to process user query
def rephrase5(user_query, response, conversation, prompts):
    if type(user_query) != str or type(response) != str or type(conversation) != str:
        return ""
    
    conv_prompt = prompts[prompts["Description"]=="Conversation control"]["Prompt"].iloc[0]
    result = conversation_control_crew(conversation, conv_prompt).kickoff()
        
    try:
        # Remove potential markdown code block syntax
        cleaned_result = str(json.loads(result.model_dump_json())['raw']).strip().replace('```json', '').replace('```', '')
        # Parse JSON response
        parsed_result = json.loads(cleaned_result)
        answer = parsed_result.get("prompt", "")

    except json.JSONDecodeError as e:
        answer = str(json.loads(result.model_dump_json())['raw']).strip().replace('```json', '').replace('```', '')

    try:
        prompt = prompts[prompts["Description"]==answer]["Prompt"].iloc[0]
    except:
        return
    
    chat_prompt = prompt.replace("{{user_query}}", user_query).replace("{{original_response}}", response).replace("{{conversation}}", conversation)
    result2 = rephraser_crew(chat_prompt).kickoff()
    try:
        # Remove potential markdown code block syntax
        cleaned_result = str(json.loads(result2.model_dump_json())['raw']).strip().replace('```json', '').replace('```', '')
        # Parse JSON response
        parsed_result = json.loads(cleaned_result)
        answer2 = parsed_result.get("answer", "")

    except json.JSONDecodeError as e:
        answer2 = str(json.loads(result2.model_dump_json())['raw']).strip().replace('```json', '').replace('```', '')
    return answer2


def rephrase_dataset(df, prompts):
    warnings.filterwarnings("ignore", message="Overriding of current TracerProvider is not allowed")
    conversation = ""
    issue = 1
    rephrased = []
    conversations = []
    for _, row in df.iterrows():
        if row["issue"] != issue:
            print("Hi")
            print(issue)
            print(row["issue"])
            conversation = ""
            issue = row["issue"]
        conversation += "User: " + str(row["User"]) + "\nResponse: " + str(row["Response"]) + "\n"
        rephrase = rephrase5(row["User"], row["Response"], conversation, prompts)
        conversations.append(conversation)
        conversation = conversation[:conversation.rfind("Response: ")]
        conversation += "Response: " + rephrase + "\n"
        rephrased.append(rephrase)

    df["conversation"] = conversations
    df["rephrased"] = rephrased
    return df