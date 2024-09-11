import openai
import pandas as pd
import chromadb
#from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()
# Set up the environment keys
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")
# Set up your OpenAI API key


# Load CSV file into DataFrame
df = pd.read_csv('updated.csv')

# Assume the CSV has a column named 'input' containing the user inputs
existing_inputs = df['User'].tolist()

# Initialize ChromaDB client
chroma_client = chromadb.Client()
#embedding_function = OpenAIEmbeddingFunction(api_key=os.environ.get('OPENAI_API_KEY'), model_name=EMBEDDING_MODEL)

# Create or get the collection in ChromaDB
collection = chroma_client.create_collection(name="user_inputs")


    

# Function to add data to ChromaDB with OpenAI embeddings
def add_to_chromadb(texts):
    for i, text in enumerate(texts):
        # Generate embedding using OpenAI API
        response = openai.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        print('response')
        embedding = response.data[0].embedding
        embedding_list = list(embedding)
        
        # Add document and embedding to ChromaDB
        collection.add(
            documents=[text],
            ids=[f"input_{i}"],
            embeddings=[embedding_list]
        )
        

# Populate ChromaDB collection if empty
if collection.count() == 0:
    add_to_chromadb(existing_inputs)

# Get new user input
new_input = '''why this amount is in pending if time out is done so refund it fast i want to send the rent. very bad service in this bank now days'''

# Generate embedding for the new input
response = openai.embeddings.create(
    input=new_input,
    model="text-embedding-ada-002"
)

new_embedding = response.data[0].embedding

# Query ChromaDB for the top 5 most similar inputs
results = collection.query(
    query_embeddings=[new_embedding],
    n_results=5
)

# Display the top 5 most similar inputs
for i, result in enumerate(results['documents'][0]):
    print(f"Rank {i+1}: {result} with similarity score: {results['distances'][0][i]}")
