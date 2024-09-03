import json
import streamlit as st
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

import storage as stg
from product import product_button


def init_crew():

    # Define search tool
    class CompanySerperDevTool(SerperDevTool):
        def search(self, query):
            company_query = f"site:https://www.oona-insurance.com {query}"
            results = super().search(company_query)
            relevant_results = [result for result in results if 'https://www.oona-insurance.com' in result.get('link', '')]
            return relevant_results

    search_tool = CompanySerperDevTool()

    # Define agents
    info_agent = Agent(
        role='Information Agent',
        goal='Retrieve the correct answer for {user_query} from internet search. Search the web once, and give the best answer you can. Summarize the information you find online.',
        backstory='''You are responsible for providing the most accurate information. Retrieve all relevant information from the internet search, and give that in a textual answer.
Do not reference urls, websites, or customer service in your answer. Just provide a summarized version of the information found online, in order to answer the question appropriately without writing too much.
Do not come up with any information or numbers that were not found online.''',
        tools=[search_tool],
        verbose=True
    )

    sales_agent = Agent(
        role='Sales Agent',
        goal='Guide customers through the insurance offerings and encourage them to purchase a suitable package while maintaining a friendly and non-pushy tone.',
        backstory='''You are designed to assist customers in finding the best coverage for their needs. Buying insurance is an important decision, so listen carefully to the customer's concerns and preferences.
Your approach is helpful and informative, aiming to build trust rather than pressure the customer. Your ultimate goal is to make the customer feel confident in their decision to purchase insurance.
Do not come up with any information or numbers yourself, just try to make a sale with provided data. Do not make too long text in your answer. Keep it concise and to the point.''',
        verbose=True
    )

    context_agent = Agent(
        role='Context Validation Agent',
        goal='Determine if the asked question is relevant to Oona Insurance, politely decline otherwise.',
        verbose=True,
        memory=True,
        backstory='''You are responsible for determining if a question is relevant to Oona Insurance. If the question is not related, 
you respond politely indicating that the question is out of context and that only Oona Insurance related information is provided.'''
    )

    conversation_agent = Agent(
        role='Conversation Control Agent',
        goal='Check what is the best next step in the conversation. Choose between giving more information, moving towards a sale, escalating the matter to a human, or ready to offer a product.',
        backstory='''You help guide a sales conversation that a prospective customer has with Oona sales bot. You decide in which direction the conversation should go next.
There are two chatbots available, the information bot and the sales bot.
If the user is asking exploratory questions and has little information about Oona Insurance, you should ask the information bot.
If the first exploratory questions have been answered, and the user is asking more specific questions, you should ask the sales bot.
If neither the information bot nor sales bot is not able to help the user, you should escalate the matter to a human.
If the user seems satisfied enough with the answers and is ready to make a purchase, you should offer a product.''',
        verbose=True
    )

    # Define task
    centralized_task = Task(
        description=f'''You get a conversation with one or multiple messages between the user and the assistant. Do the following tasks:
First, determine if {{user_query}} is relevant to Oona Insurance, by asking the context validator agent, and respond appropriately.
Second, check what should happen with the conversation after this answer. Conversation: {{conversation}}. Ask the conversation control agent if the conversation should continue with information, move towards a sale, escalate to a human, or you offer a product.
If the query is about Oona Insurance and the conversation is in the first informative phase, provide a detailed and informative response, by asking the information agent to search the web and retrieve information. Provide a summarized version of this information that answers the question, do not use too many sentences.
If the query is about Oona Insurance and the user is ready to talk about a sale, provide a response that moves the conversation towards a sale, by asking the sales agent to make a sales pitch.
Always ask either the information bot or the sales bot, do not come up with an answer yourself. Do not come up with any information or numbers that were not found online.
If the conversation should be escalated or a product offer, simply provide an appropriate final response, without providing any additional information.''',
        expected_output='''A JSON object containing "answer" and "control". "answer" should contain text with the answer to follow the conversation, and "control" one out of three categories: 'continue', 'human' or 'product'.
Output json without any unescaped newline characters and without any codeblock. The response should be able to pass JSON.loads() without any error.
Text output for "answer" should be able to render in markdown, using appropriate notation and newlines for lists, do not use other markdown elements aside from lists.''',
        agent=Agent(
            role='Oona Insurance Sales Bot',
            goal=f'Manage a sales conversation about Oona Insurance and its offerings.',
            verbose=True,
            memory=True,
            backstory=('''You are an intelligent bot specializing in Oona Insurance information. You provide detailed responses about Oona Insurance. 
You only respond to queries related to Oona Insurance. Delegate tasks to helpers as needed. Always check if the user query is relevant to Oona Insurance.
Always check with the conversation control agent to see what the next step in the conversation should be.
If additional information is required to give your answer, ask the information agent. If initial information has been given, ask the sales agent to move towards a sale.
Formulate your final answer so that it is always appropriate to present the user. Do not refer to any urls, websites or customer service in your answer. If your answer contains lists or subtitles, add appropriate markdown elements to render.'''),
            allow_delegation=True
        )
    )

    info_agent.allow_delegation = False
    context_agent.allow_delegation = False
    conversation_agent.allow_delegation = False

    # Init crew
    conversation_crew = Crew(
        agents=[context_agent, info_agent, sales_agent, conversation_agent],
        tasks=[centralized_task],
        process=Process.sequential  # Executes tasks in sequence
    )

    return conversation_crew


def conversation_history():
    # Make a string containing all messages in current history
    history = ''
    for message in st.session_state.messages:
        history += f"{message['role']}: {message['content']}\n"
    return history


# Function to process user query
def process_query(user_query):
    if user_query.lower() == "give me today logs 420":
        stg.download_current_logs()
        return
    if user_query.lower() == "give me all logs 420":
        stg.download_all_logs()
        return
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    answer = ""  # Initialize the answer variable

    with st.chat_message("assistant"):
        with st.spinner("Processing your input..."):
            crew = init_crew()
            result = crew.kickoff(inputs={'user_query': user_query, 'conversation': conversation_history()})
            try:
                # Remove potential markdown code block syntax
                cleaned_result = str(json.loads(result.model_dump_json())['raw']).strip().replace('```json', '').replace('```', '')
                print(json.loads(result.model_dump_json())['raw'])
                # Parse JSON response
                parsed_result = json.loads(cleaned_result)
                answer = parsed_result.get("answer", "")
                control = parsed_result.get("control", "")
                st.markdown(f"{answer}")

                # Update follow-up questions in session state
                st.session_state.control = control

            except json.JSONDecodeError as e:
                print(e)
                st.markdown(f"**Error parsing JSON:**\n{result}")
                answer = "There was an error processing your request."

    st.session_state.messages.append({"role": "assistant", "content": answer})

    # Save chat history to file
    stg.save_chat_history()
    st.rerun()


def salesbot():
    st.markdown("""
        
        <h1 style="color:#9b51e0;">
            OONA Sales
        </h1>
    
    """, unsafe_allow_html=True)
    st.write("<style>div.block-container{padding-top:2rem;}</style>", unsafe_allow_html=True)

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input at the bottom of the page
    user_input = st.chat_input(f"Enter your question about Oona Insurance:")

    if user_input:
        process_query(user_input)

    if len(st.session_state.messages) == 1:
        for category in ["Car insurance", "Travel insurance", "Health insurance", "CTPL"]:
            if st.button(category):
                process_query(f"Tell me more about {category}")

    if "control" in st.session_state:
        if st.session_state.control.lower() == 'human':
            if st.button("Speak to a human", help="If you prefer to speak with a human, click here. Else, keep talking in the chat."):
                st.markdown("Chat ends. Here speak to a human")
        if st.session_state.control.lower() == 'product':
            if st.button("Go to product", help="If you are ready to purchase a product, click here. Else, keep talking in the chat."):
                product_button()