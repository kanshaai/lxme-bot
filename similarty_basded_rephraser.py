import chromadb
import pandas as pd
import google.generativeai as genai
import os
import time
import google.generativeai as genai
import streamlit as st

# Set up your environment variable for the API key
genai.configure(api_key='AIzaSyAhh1f5YAVcvBwvnIFL9ZSowBTXLnrE1G0')



# Gemini model setup
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initialize the Gemini model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="Understand the manner in which we rephrase the response from the file shared and your job is to rephrase the new queries given to you.",
)

chroma_client = chromadb.Client()



df = pd.read_csv('updated.csv')
existing_inputs = df['User'].tolist()
number_list = ['id'+str(i) for i in range(len(existing_inputs))]

collection = chroma_client.create_collection(name="my_collection")
collection.add(
    documents= existing_inputs,
    ids=number_list
)

def get_similar(user_input):
    results = collection.query(
        query_texts=[user_input], # Chroma will embed this for you
        n_results=5 # how many results to return
    )
    print()
    return results['documents'][0]

Examples = ""




st.title("Rephrase Customer Queries Using Similarity")
user_query = st.text_area("Enter the customer query:", key="query_input_tab1")
original_response= st.text_area("Enter the original response:", key="response_input_tab1")
if st.button("Rephrase Response (Query & Response)"):
    with st.spinner("Processing your input..."):


        User_query = user_query
        original_response = original_response
        results = get_similar(User_query)
        print(results)
        for index, row in df.iterrows():
            if row['User'] in results:
                User_query = row['User']
                original_response = row['Response']
                rephrased_response = row['response1']  ###Riddhi's Response will come here later on
                Examples = Examples + "User Query: " + User_query + '\n' + "Original Response:" + original_response + '\n' + "Rephrased Response:" + rephrased_response

        chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    
                    f"Understand the manner in which we rephrase the response from the {Examples} shared and your job is to rephrase the new queries given to you.",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "Okay, I understand. You want me to rephrase responses to customer queries based on the pattern you've shown. I will not mention names until specified in query or actual response.",
                ],
            },
        ]
        )



        response = chat_session.send_message(f"query: {User_query}\n\nresponse: {original_response}\n\nJust send back the rephrased response.")
        st.write("Rephrased Version")
        st.write(response.text)


