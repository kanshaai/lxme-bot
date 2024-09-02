import json
import streamlit as st
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

from storage import save_chat_history


def init_crew():
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
        goal='Retrieve the correct answer for {user_query} from internet search. Just search the web once, and give the best answer you can. Do not keep searching further after the first time.',
        backstory='You are responsible for providing the most accurate information.',
        tools=[search_tool],
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
        goal='Check what is the best next step in the conversation. Choose between continuing the conversation with salesbot, escalating the matter to a human, or ready to offer a product.',
        backstory='''You help guide a sales conversation that a prospective customer has with Oona sales bot. You decide in which direction the conversation should go next.
If the conversation is following a normal course, with informed questions and answers, you should continue the conversation.
If the assistant sales bot is not able to help the user, you should escalate the matter to a human.
If the user seems satisfied enough with the answers and is ready to make a purchase, you should offer a product.''',
        verbose=True
    )


    centralized_task = Task(
        description=f'You get a conversation with one or multiple messages between the user and the assistant. Do the following tasks:'
        f'First, determine if {{user_query}} is relevant to Oona Insurance, by asking the context validator agent, and respond appropriately.'
        f'Second, check what should happen with the conversation after this answer. Conversation: {{conversation}}. Ask the conversation control agent if the conversation should continue, it should escalate to a human, or you offer a product.'
        f'If the query is about Oona Insurance and the conversation should continue, provide a detailed and informative response, by asking the information agent to search the web and retrieve information.'
        f'If the conversation should be escalated or a product offer, simply provide an appropriate final response, without providing any additional information.',
        expected_output='''A JSON object containing "answer" and "control". "answer" should contain text with the answer to follow the conversation, and "control" one out of three categories: 'continue', 'human' or 'product'.
    Output json without any unescaped newline characters and without any codeblock. The response should be able to pass JSON.loads() without any error.''',
        agent=Agent(
            role='Oona Insurance Sales Bot',
            goal=f'Manage a sales conversation about Oona Insurance and its offerings.',
            verbose=True,
            memory=True,
            backstory=('''You are an intelligent bot specializing in Oona Insurance information. You provide detailed responses about Oona Insurance. 
    You only respond to queries related to Oona Insurance. Delegate tasks to helpers as needed. Always check if the user query is relevant to Oona Insurance.
    Always check with the conversation control agent to see what the next step in the conversation should be. If additional information is required to give your answer, ask the information agent.
    Formulate your final answer so that it is always appropriate to present the user.'''),
            tools=[search_tool],
            allow_delegation=True
        )
    )

    info_agent.allow_delegation = False
    context_agent.allow_delegation = False
    conversation_agent.allow_delegation = False

    conversation_crew = Crew(
        agents=[context_agent, info_agent, conversation_agent],
        tasks=[centralized_task],
        process=Process.sequential  # Executes tasks in sequence
    )

    return conversation_crew


def conversation_history():
    history = ''
    for message in st.session_state.messages:
        history += f"{message['role']}: {message['content']}\n"
    return history


# Function to process user query
def process_query(user_query):
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
    save_chat_history()
    st.rerun()


def salesbot():
    st.markdown("""
        
        <h1 style="color:#9b51e0;">
            OONA Sales
        </h1>
    
    """, unsafe_allow_html=True)
    left, right = st.columns([8, 2])
    with left:
        st.write("<style>div.block-container{padding-top:2rem;}</style>", unsafe_allow_html=True)
    with right:
        st.button("Background info", on_click=lambda: st.session_state.update(page="infopage"))

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
            st.button("Go to product", help="If you are ready to purchase a product, click here. Else, keep talking in the chat.", on_click=lambda: st.session_state.update(page="infopage"))
