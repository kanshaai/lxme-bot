import json
import os
import streamlit as st
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
from pathlib import Path
import db
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Set up the environment keys
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

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



prompts = {
    "Use 'You' Focus Sentences": "Rephrase the original text by centering the response around the user's needs and concerns. Start sentences with 'You' or phrases that emphasize the user’s perspective.",
    
    "Validate User's Urgency": "Rephrase the original text to acknowledge the user's urgency and demonstrate understanding of the importance of resolving the issue quickly. Express empathy and urgency in your response.",
    
    "Choose Words Carefully": "Rephrase the original text by selecting words that convey a sense of action, urgency, and reassurance. Avoid words that might trigger negative emotions or increase anxiety. Use more positive and proactive language.",
    
    "End with Solution Orientation": "Rephrase the original text to ensure that the response ends with a clear focus on the next steps and the actions being taken to resolve the issue. Emphasize what will be done to address the user's concern.",
    
    "Minimize User Effort": "Rephrase the original text to avoid asking the user to take additional steps. Emphasize that you will handle everything and proactively keep them updated without requiring them to follow up.",
    
    "Avoid Over-Apologizing": "Rephrase the original text to show empathy without excessive apologies. Focus on taking action and providing solutions rather than over-apologizing, which can seem insincere or increase annoyance.",
    
    "Use Presuppositions": "Rephrase the original text by stating facts confidently without seeking confirmation from the user. Increase assurance by presenting the situation as something that is already being handled.",
    
    "Limit Apologies": "Rephrase the original text to limit apologies and maintain professionalism. Focus on resolving the issue without accepting fault unless it’s necessary. Keep the tone positive and proactive.",
    
    "Reframe the Issue": "Rephrase the original text to present the situation in a way that shifts focus from any potential fault of the service provider to finding a resolution. Highlight the steps being taken to fix the problem rather than dwelling on the issue itself.",
    
    "Redirect Blame": "Rephrase the original text to subtly shift responsibility away from the service provider without directly blaming others. Focus on external factors like system processes or banking protocols to explain the situation."
}

def understand_tactics(user_input, sprinklr_input):
    # Call OpenAI API to understand user's emotion and generate a prompt
    response =client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that understands emotions. "},
            {"role": "user", "content": f'''

I need you to generate a list of tactics that should be used when rephrasing this where
the user query is : {user_input} 
the original response is : {sprinklr_input}
These tactics should focus on improving communication, managing user expectations, and maintaining a positive tone while avoiding blame or excessive apologies. Please provide the list in Python list format.
You should not accept your mistake anytime, you have to acknowledge user only when this is someone else's mistale.
Each tactic should focus on a specific communication strategy. You should choose the tactics from the following:tactics = [
    "Use 'You' Focus Sentences",
    "Validate User's Urgency",
    "Choose Words Carefully",
    "End with Solution Orientation",
    "Minimize User Effort",
    "Avoid Over-Apologizing",
    "Use Presuppositions",
    "Limit Apologies",
    "Reframe the Issue",
    "Redirect Blame"
]
Your output should be just a single python list with all the tactics




'''}
        ]
    )
    prompt = response.choices[0].message.content
    
    return prompt


def generate_prompt(tactics_list):
    combined_prompt = []
    
    for tactic in tactics_list:
        if tactic in prompts:
            combined_prompt.append(prompts[tactic])
        else:
            combined_prompt.append(f"No prompt available for the tactic: {tactic}")
    
    # Join all prompts into a single string
    return "\n\n".join(combined_prompt)


def rephrase_sprinklr(sprinklr_input, generated_prompt, tactics_prompt):
    # Call OpenAI API to rephrase the Sprinklr input using the generated prompt
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that rephrases text."},
            {"role": "user", "content": f'''

             Chatbot Response: {sprinklr_input} 
             User's emotions: {generated_prompt}            
Rephrase the chatbot's response to address the user's emotions in a way that fosters trust, validation, and hope, while reducing feelings of anger or fear. Separate content from delivery, focusing on what needs to be communicated and how it should be conveyed. Ensure the message is clear, concise, and actionable to minimize cognitive overload for the user.
You should never say sentences like you don't need to, it looks like you are making an order, always use don't need to worry like sentences which gives user hope that we also worry about him.
Maintain a conversational and friendly tone throughout, ensuring that the rephrased message never becomes helpless, apologetic, or defensive. Avoid justifying or explaining any inconvenience, pain, or anger caused to the user, and concentrate on what can be done now to resolve the issue.

Your response should be concise, and if possible use bullet points for steps or important information.
Reflect the user's emotions and concerns to build rapport and demonstrate understanding, mirroring their frame of mind. Always maintain a solution-oriented approach by providing clear next steps and timelines, reducing uncertainty and anxiety.
{tactics_prompt}



'''}
        ]
    )
    rephrased_output = response.choices[0].message.content
    return rephrased_output



def rephrase_sprinklr_with_history(sprinklr_input, generated_prompt, tactics_prompt, conversation_history):
    # Create a list of message objects for each part of the conversation history
    messages = [{"role": "system", "content": "You are an assistant that rephrases text."}]

    # Add conversation history as alternating 'user' and 'assistant' messages
    for entry in conversation_history:
        messages.append({"role": "user", "content": f"User: {entry['user']}"})
        messages.append({"role": "assistant", "content": f"Response: {entry['response']}"})

    # Add the current user emotion and Sprinklr input to the message sequence
    messages.append({"role": "user", "content": f"Chatbot Response: {sprinklr_input}"})
    messages.append({"role": "user", "content": f"User's emotions: {generated_prompt}"})

    # Include the rephrasing instructions
    messages.append({"role": "user", "content": f'''
        Rephrase the chatbot's response to address the user's emotions in a way that fosters trust, validation, and hope, while reducing feelings of anger or fear. 
        Separate content from delivery, focusing on what needs to be communicated and how it should be conveyed. 
        Ensure the message is clear, concise, and actionable to minimize cognitive overload for the user.
        Maintain a conversational and friendly tone, and avoid justifying or explaining any inconvenience caused to the user.
        {tactics_prompt}
If you have acknowledged user's emotions or emergency once in the conversation history, there is no need to do it again. Even if it is their in chatbot response no need to add this in your response.


Important points to remember:
While giving your final response, take care of conversation history, don't repeat yourself if you have said something before never say it again. It should be a conversation going on between two people. Do not repeat sentences like "lets work together", "rest assured" , "I understand " etc.
Use formal words, like do not use ASAP use swiftly instead.
Do not overexplain anything.
Your final response should not ask user for any transaction details or recipent details, assume you already have that.

    '''})

    # Call the OpenAI API with the constructed messages
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    
    rephrased_output = response.choices[0].message.content
    return rephrased_output





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


def conversation_control_crew():
    description = db.get_control_prompt()["prompt"].iloc[0]
    description = description.replace("{{conversation}}", conversation_history(st.session_state.messages))
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


def rephraser_crew():
    centralized_task = Task(
        description=st.session_state.chat_prompt,
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
        

        if answer2 in ['Frustrated','Angry','Impatient','Threatening']:
            user_emotions = understand_tactics(user_query, answer1)
            
            tactic_prompt = generate_prompt(user_emotions)
            st.session_state.messages.append({"role": "Tactic", "content":user_emotions})
    st.session_state.messages.append({"role": "Control", "content": answer2})

    with st.chat_message("assistant"):
        with st.spinner("Rephrasing the answer..."):
            if answer2 in ['Frustrated','Angry','Impatient','Threatening']:
                answer3 = rephrase_sprinklr(answer1, user_query, tactic_prompt)
            else:
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


def render_chat_mvp():
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