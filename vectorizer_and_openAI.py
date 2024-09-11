import streamlit as st
import openai
import os
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import time

def get_embedding(text):
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    embedding = response.data[0].embedding
    
    return np.array(embedding)




def find_similarity_using_vectorizer(user_input):
    df = pd.read_csv('updated.csv')
    existing_inputs = df['User'].tolist()
    new_input = user_input
    start_time = time.time()
    vectorizer = TfidfVectorizer()
    all_inputs = existing_inputs + [new_input]
    tfidf_matrix = vectorizer.fit_transform(all_inputs)
    similarity_matrix = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    similarities = similarity_matrix.flatten()
    top_5_indices = similarities.argsort()[-5:][::-1]
    end_time = time.time()
    time_taken = end_time - start_time
    st.write("Vectorizer embeddings")
    st.write(f"Time Taken: {time_taken:.2f}")
    for i in top_5_indices:
        
        st.write(f"Similar Input: {existing_inputs[i]} - Similarity Score: {similarities[i]}")

    return



def find_similarity_using_openai(user_input):
    df = pd.read_csv('updated.csv')
    existing_inputs = df['User'].tolist()
    new_input = user_input
    start_time = time.time()
    existing_embeddings = np.array([get_embedding(text) for text in existing_inputs])
    new_input_embedding = np.array(get_embedding(new_input)).reshape(1, -1)
    similarities = cosine_similarity(new_input_embedding, existing_embeddings).flatten()

    # Get the top 5 most similar inputs
    top_5_indices = similarities.argsort()[-5:][::-1]
    end_time = time.time()
    time_taken = end_time - start_time
    st.write("OpenAI embeddings")
    st.write(f"Time Taken: {time_taken:.2f}")
    for i in top_5_indices:
        #print(f"Similar Input: {existing_inputs[i]} - Similarity Score: {similarities[i]}")


   

        st.write(f"Similar Input: {existing_inputs[i]} - Similarity Score: {similarities[i]}")
    return 


# Load environment variables from .env file
load_dotenv()
# Set up the environment keys
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

def understand_user(user_input):
    # Call OpenAI API to understand user's emotion and generate a prompt
    response =client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that understands emotions. "},
            {"role": "user", "content": f"The user says: {user_input}. What is their emotion"}
        ]
    )
    prompt = response.choices[0].message.content
    
    return prompt


def rephrase_sprinklr(sprinklr_input, generated_prompt):
    # Call OpenAI API to rephrase the Sprinklr input using the generated prompt
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that rephrases text."},
            {"role": "user", "content": f'''

             Chatbot Response: {sprinklr_input} 
             User's emotions: {generated_prompt}            
Rephrase the chatbot's response to address the user's emotions in a way that fosters trust, validation, and hope, while reducing feelings of anger or fear. Separate content from delivery, focusing on what needs to be communicated and how it should be conveyed. Ensure the message is clear, concise, and actionable to minimize cognitive overload for the user.

Reflect the user's emotions and concerns to build rapport and demonstrate understanding, mirroring their frame of mind. Always maintain a solution-oriented approach by providing clear next steps and timelines, reducing uncertainty and anxiety.

Use 'You'-focused sentences to center on the user's needs and concerns (e.g., 'Let's focus on getting this resolved for you'). Choose words that convey action, urgency, and reassurance, while avoiding terms that might trigger negative emotions or increase anxiety.

Validate the user's urgency and importance of a timely resolution (e.g., 'I understand that you need this resolved quickly'). Avoid over-apologizing; instead, emphasize taking action and providing solutions. Start sentences with 'Yes' to create a more agreeable tone, even when disagreeing.

End with a focus on the solution, clearly outlining the next steps and emphasizing what actions are being taken to resolve the issue. Use presuppositions to state facts confidently, reducing uncertainty (e.g., 'Your money is safe' instead of 'Please be assured your money is safe'). Minimize the user's effort by avoiding requests for additional steps or follow-ups, and emphasize proactive communication to keep them updated.

Maintain a conversational and friendly tone throughout, ensuring that the rephrased message never becomes helpless, apologetic, or defensive. Avoid justifying or explaining any inconvenience, pain, or anger caused to the user, and concentrate on what can be done now to resolve the issue.

Your response should be concise, and if possible use bullet points for steps or important information.

Only give the rephrased reponse nothing else.

'''}
        ]
    )
    rephrased_output = response.choices[0].message.content
    return rephrased_output

# Streamlit app
st.title("Emotion-based Sprinklr Rephraser")

# User input
user_input = st.text_input("Enter User Input:")
sprinklr_input = st.text_area("Enter Sprinklr Input:")

if st.button("Submit"):
    if user_input and sprinklr_input:
        with st.spinner("Processing..."):
            # Step 1: Generate prompt based on user input
            find_similarity_using_vectorizer(user_input)
            find_similarity_using_openai(user_input)


            user_emotions = understand_user(user_input)
            

            # Step 2: Rephrase Sprinklr input using the generated prompt
            rephrased_output = rephrase_sprinklr(sprinklr_input, user_emotions)
            st.write("Rephrased Sprinklr Output:")
            st.write(rephrased_output)
    else:
        st.error("Please provide both User and Sprinklr inputs.")