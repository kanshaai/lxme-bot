import streamlit as st
import json
import streamlit as st
from crewai import Agent, Task, Crew, Process


def conversation_history():
    history = ''
    for message in st.session_state.messages:
        if message['role'] == 'user':
            history += f"User: {message['content']}\n"
    return history


def info_crew():

    evaluator_agent = Agent(
        role='Oona Insurance Sales Evaluator',
        goal=f'Evaluate a sales conversation about Oona Insurance, determine the products the user is interested in.',
        verbose=True,
        memory=True,
        backstory=('''You are an intelligent bot specializing in sales conversations. After a conversation has been concluded, you are to
evaluate product the user might be interested in.''')
    )

    centralized_task = Task(
        description=f'''You get a conversation with one or multiple messages between a user and a sales assistant. {{conversation}} Do the following tasks:
Determine which product the user is interested in. There are five categories of products: Car insurance, Travel insurance, Health insurance, CTPL (compulsory third party liability)
or other. If you are unsure in which category the product falls, just choose other. If the user talks about multiple products, list all of those products.
Output a list of interested products.''',
        expected_output='''A JSON object containing key and "product".
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


def product_button():
    st.info('''By proceeding to the product, currently we provide a link to the appropriate product page.
In a more evolved version, the salesbot will directly ask the user to input certain personal details into the chat,
and then prefill these details and redirect the user to a page with a quotation ready to purchase.''')
    with st.spinner("Preparing product page"):
        crew = info_crew()
        evaluation = crew.kickoff(inputs={"conversation": conversation_history()})
        try:
            # Remove potential markdown code block syntax
            cleaned_result = str(json.loads(evaluation.model_dump_json())['raw']).strip().replace('```json', '').replace('```', '')
            print(json.loads(evaluation.model_dump_json())['raw'])
            # Parse JSON response
            parsed_result = json.loads(cleaned_result)
            product = parsed_result.get("product", "")

        except json.JSONDecodeError as e:
            print(e)
            st.markdown(f"**Error parsing JSON:**\n{evaluation}")
            product = ''

    if "car" in product:
        st.markdown('Purchase car insurance: https://myoona.ph/all-product/car-insurance/')
    if "travel" in product:
        st.markdown('Purchase travel insurance: https://myoona.ph/all-product/travel-insurance/')
    if "health" in product:
        st.markdown('Purchase health insurance: https://myoona.ph/all-product/critical-illness-insurance/')
    if "ctpl" in product:
        st.markdown('Purchase CTPL insurance: https://myoona.ph/all-product/ctpl-insurance/')
    if "other" in product:
        st.markdown('Browse Oona insurance to make a purchase: https://www.oona-insurance.com')