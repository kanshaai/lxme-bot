import streamlit as st
import os
from dotenv import load_dotenv
import numpy as np
from streamlit_chromadb_connection.chromadb_connection import ChromadbConnection
import pandas as pd
import google.generativeai as genai




load_dotenv()
# Set up the environment keys
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

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

configuration = {
    "client": "PersistentClient",
    "path": "/tmp/.chroma"
}




conn = st.connection("chromadb",
                     type=ChromaDBConnection,
                     **configuration)



df = pd.read_csv('updated.csv')
existing_inputs = df['User'].tolist()
number_list = ['id'+str(i) for i in range(len(existing_inputs))]

collection = conn.create_collection(name="my_collection")
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