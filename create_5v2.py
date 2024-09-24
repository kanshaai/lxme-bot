import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
import db
import os
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Set up the environment keys
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

# Initialize the OpenAI client
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

def feedback(user_message, original_response, rephrased_version, conversation):
    response =client.chat.completions.create(
        model="gpt-4o",
       
        messages=[
           

{"role": "user", "content": f''' User query : {user_message}
                                 original response: {original_response}
 
                                 Rephrased version : {rephrased_version}
                                 conversation: {conversation}
in above, rewrite the rephraser version by incorporating this
- don't add any new information which is not present in original response
- don't say any annoying phrases like "don't worry" or "I understand"
- don't apologise - they're meaningless
- don't make promises a customer support agent cannot keep if the business teams work a certain way
- use opportunities where possible to agree with what the user needs or values
- make user feel you understand them without saying you do. saying is annoying as it feels like a lie
- In any conversation if you have acknowledged user once, don't do it again and again
- user could be lying while frustrated at customer support ---- acknowledge their assessment of their good habits without saying it in a way that makes it seem you have checked their actual records and are putting your stamp of agreement on that assessment. that could get the company in trouble if their actual account activity with the company is not great

*rewrite the original response from above, and ensure to give just the response nothing else

 
'''}
        ]
    )
    response = response.choices[0].message.content
    
    return response


def rephraser(user_message, original_response):
    response =client.chat.completions.create(
        model="ft:gpt-4o-2024-08-06:kansha::A9shP940",
        temperature=1,
        messages=[
           

{"role": "user", "content": f''' User query : {user_message}
                                 original response: {original_response}
                                 
Make this response perfect and just give the new response as output nothing else so i can just add it to a file directly


 
'''}
        ]
    )
    response = response.choices[0].message.content
    
    return response



def rephrase_dataset(df):
    issue = 1

    for index, row in df.iterrows():
        
            if row["issue"] != issue:
                conversation = ""
                issue = row["issue"]
            conversation += "User: " + str(row["User"]) + "\nResponse: " + str(row["Response"]) + "\n"
            rephrase = rephraser(row["User"], row["Response"])
            rephrase_with_feedback = feedback(row['User'],row["Response"], rephrase, conversation )
            print(rephrase_with_feedback)
            df.at[index, 'rephrased_5v1'] = rephrase_with_feedback
            df.to_csv('Full rephrased1201.csv', index=False)
            print(f'{index} done')


        
            

df = pd.read_csv('Full rephrased - New Feedbacks (19 Sep Thurs) (2).csv')
rephrase_dataset(df)