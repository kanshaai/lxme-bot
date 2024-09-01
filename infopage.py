import streamlit as st
import json
import streamlit as st
from crewai import Agent, Task, Crew, Process


def conversation_history():
    history = ''
    for message in st.session_state.messages:
        history += f"{message['role']}: {message['content']}\n"
    return history


def info_crew():

    evaluator_agent = Agent(
        role='Oona Insurance Sales Evaluator',
        goal=f'Evaluate a sales conversation about Oona Insurance, determine the category of user and products they are interested in.',
        verbose=True,
        memory=True,
        backstory=('''You are an intelligent bot specializing in sales conversations. After a conversation has been concluded, you are to
evaluate whether the user is likely to buy a product or not, and which products they might be interested in.''')
    )

    centralized_task = Task(
        description='''You get a conversation with one or multiple messages between a user and a sales assistant. {{conversation}} Do the following tasks:
Classify how likely the user is to become a customer. Read the entire chat history between the user and the sales assistant, and determine whether the
user falls into one of three categories: not ready to buy, maybe ready to buy but needs more information or time, or ready to buy. Always classify into one of these three categories.
Second, try to determine which product the user is interested in. There are five categories of products: Car insurance, Travel insurance, Health insurance, CTPL (compulsory third party liability)
or other. If you are unsure in which category the product falls, just choose other. If the user talks about multiple products, list all of those products.
Output both the category of user, and a list of interested products.''',
        expected_output='''A JSON object containing keys "category" and "product". "category" should contain text with exactly one of three: "not_ready", "maybe_ready", "ready".
"product" should contain a list of values (even if the list is empty), choose from: "car", "travel", "health", "ctpl" or "other".
Output json without any unescaped newline characters and without any codeblock. The response should be able to pass JSON.loads() without any error. Do not deviate values in your output from the available values given here.''',
        agent=evaluator_agent
    )

    crew = Crew(
        agents=[evaluator_agent],
        tasks=[centralized_task],
        process=Process.sequential  # Executes tasks in sequence
    )

    return crew


def infopage():
    st.markdown("""
        <h1 style="color:#9b51e0;">
            Background information page
        </h1>
    """, unsafe_allow_html=True)
    left, right = st.columns([8, 2])
    with left:
        st.write("<style>div.block-container{padding-top:2rem;}</style>", unsafe_allow_html=True)
    with right:
        st.button("Sales bot", on_click=lambda: st.session_state.update(page="salesbot"))
    st.info("""The following information is gathered from the conversation history between the user and the assistant.
It should not be shown to the user. Instead it should connect to the backend of the system, in order to enter the user into the CRM, 
and redirect to a specific product page with a quotation of the requested service.""")

    with st.spinner("Evaluating the conversation..."):
        crew = info_crew()
        evaluation = crew.kickoff(inputs={"conversation": conversation_history()})
        try:
            # Remove potential markdown code block syntax
            cleaned_result = str(json.loads(evaluation.model_dump_json())['raw']).strip().replace('```json', '').replace('```', '')
            print(json.loads(evaluation.model_dump_json())['raw'])
            # Parse JSON response
            parsed_result = json.loads(cleaned_result)
            category = parsed_result.get("category", "")
            product = parsed_result.get("product", "")

        except json.JSONDecodeError as e:
            print(e)
            st.markdown(f"**Error parsing JSON:**\n{evaluation}")
            category = ''
            product = ''

    left, right = st.columns(2)
    with left:
        st.header("User evaluation", help="Evaluation how much the user might be interested to buy a product based on initial conversation.")
        if category == "not_ready":
            st.markdown("The user is not ready to buy a product.")
        elif category == "maybe_ready":
            st.markdown("The user might be ready to buy a product, but needs more information or time.")
        elif category == "ready":
            st.markdown("The user is convinced to buy a product, and will do it soon.")
    with right:
        st.header("Product of interest", help="Selection of products the user might be interested in.")
        if "car" in product:
            st.markdown('Purchase ar insurance: https://myoona.ph/all-product/car-insurance/')
        if "travel" in product:
            st.markdown('Purchase travel insurance: https://myoona.ph/all-product/travel-insurance/')
        if "health" in product:
            st.markdown('Purchase health insurance: https://myoona.ph/all-product/critical-illness-insurance/')
        if "ctpl" in product:
            st.markdown('Purchase CTPL insurance: https://myoona.ph/all-product/ctpl-insurance/')
        if "other" in product:
            st.markdown('Browse Oona insurance to make a purchase: ')