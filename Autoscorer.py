import streamlit as st
import openai
import os
from dotenv import load_dotenv
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import time
import pandas as pd
from io import BytesIO
from sklearn.feature_extraction.text import TfidfVectorizer


def find_similarity_using_vectorizer(rephrase_response, riddhi_response):
    # Initialize the vectorizer
    vectorizer = TfidfVectorizer()
    
    # Fit and transform the responses into TF-IDF vectors
    tfidf_matrix = vectorizer.fit_transform([rephrase_response, riddhi_response])
    
    # Calculate the cosine similarity between the two vectors
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    
    return similarity





#### Just adding this code here if you want to find similarity score using OpenAI embeddings (they are slow and paid)
def get_embedding(text):
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    embedding = response.data[0].embedding
    print(embedding)
    return np.array(embedding)

def calculate_similarity(embedding1, embedding2):
    return cosine_similarity([embedding1], [embedding2])[0][0]






df = pd.read_csv('updated.csv')
for index, row in df.iterrows():
    df.at[index, 'r1_score'] = find_similarity_using_vectorizer(row['response1'],row['response2']) ####In place of response 2 we need to add Riddhi's Resposne
    df.at[index, 'r2_score'] = find_similarity_using_vectorizer(row['response2'],row['response2'])
    ##### add as many as you want
    print(index)

    
df.to_csv('update5.csv',index=False) ### you can append it same csv or use a different one


