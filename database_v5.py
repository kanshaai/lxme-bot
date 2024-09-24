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

def continue_conversation(messages):
    response = client.chat.completions.create(
        model="gpt-4o",  # Assuming you're using GPT-4o-mini model
        messages=messages
    )
    return response.choices[0].message.content

df = pd.read_csv('customer_service_issues10 - customer_service_issues10.csv')

conversations = df.groupby('issue').apply(
    lambda x: '\n\n'.join([f"User: {row['User']}\nResponse: {row['Response']}" for _, row in x.iterrows()])
).reset_index(name='Conversation')

for index, row in conversations.iterrows():
    if index<54:
        continue



    conversation = row['Conversation']

    messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": f'''conversation: {conversation}
                                                   
                                                   
                                                   '''}
    ]

    # Add the next prompt for the continuation of the conversation
    user_followup = "what are 5 specific things that if improved in above customer service conversation with a user, would actually help the user be more satisfied"

    # Append user follow-up to messages
    messages.append({"role": "user", "content": user_followup})

    # Send the conversation to OpenAI and get the response
    response_content = continue_conversation(messages)

    # Print the response from the model
    print("Response from model: \n", response_content)
    messages.append({"role": "system", "content": response_content})

    # You can continue adding more user prompts like this:
    new_user_input = '''rewrite the entire conversation attached above, again below, after incorporating all above recognised improvements
    and ensure you don't sound disingenous in anyway'''
    messages.append({"role": "user", "content": new_user_input})

    # Get the next part of the conversation
    updated_response = continue_conversation(messages)
    messages.append({"role": "system", "content": updated_response})
    # Print the next response
    print("Updated conversation: \n", updated_response)

    new_user_input_2 = '''what are 5 specific things that if improved in above customer service conversation with a user, would actually help the user be more satisfied'''
    messages.append({"role": "user", "content": new_user_input_2})

    updated_response_2 = continue_conversation(messages)
    messages.append({"role": "system", "content": updated_response_2})
    # Print the next response
    #print("Updated conversation 2: \n", updated_response_2)

    new_user_input_3 = '''rewrite the entire conversation attached above, again below, after incorporating all above recognised improvements
    and ensure you don't sound disingenous in anyway'''
    messages.append({"role": "user", "content": new_user_input_3})

    updated_response_3 = continue_conversation(messages)
    messages.append({"role": "system", "content": updated_response_3})
    # Print the next response
    #print("Updated conversation 3: \n", updated_response_3)

    new_user_input_4 = '''rate the above conversation from 1 (criminal) to 10 (unbelievable) basis how Ron Kaufman would rate it'''
    messages.append({"role": "user", "content": new_user_input_4})

    updated_response_4 = continue_conversation(messages)
    messages.append({"role": "system", "content": updated_response_4})
    # Print the next response
    #print("Updated conversation 4: \n", updated_response_4)


    new_user_input_5 = f'''in above, rewrite the conversation by incorporating this
- don't say any annoying phrases like "don't worry" or "I understand"
- don't over apologise - they're meaningless
- don't make promises a customer support agent cannot keep if the business teams work a certain way
- use opportunities where possible to agree with what the user needs or values
- make user feel you understand them without saying you do. saying is annoying as it feels like a lie
- In any conversation if you have acknowledged user once, don't do it again and again
- user could be lying while frustrated at customer support ---- acknowledge their assessment of their good habits without saying it in a way that makes it seem you have checked their actual records and are putting your stamp of agreement on that assessment. that could get the company in trouble if their actual account activity with the company is not great

*rewrite the entire conversation from above, again below, after incorporating all above recognised improvements
and ensure you don't sound disingenous in anyway*


    '''
    messages.append({"role": "user", "content": new_user_input_5})

    updated_response_5 = continue_conversation(messages)
    messages.append({"role": "system", "content": updated_response_5})
    # Print the next response
    #print("Final Output : \n", updated_response_5)

    new_user_input_6 = f'''

 convert the above conversation in such a way that it can be converted to a csv file directly. The format should be like. Add a row issue where issue is {row['issue']}
    issue, user, response
    "issue name","user message","response"
    "issue name","user message","response"
    "issue name","user message","response"
    "issue name","user message","response"
    "issue name","user message","response"
    "issue name","user message","response"
    "issue name","user message","response"



    Make sure the csv structure is maintained properly. Since We're using \" for values, make sure they dont appear in messages as they affect the csv format and make it non usuable. Also make sure customer is showing immense emotions and even threats sometimes. IMPORTANT  : MAKE SURE CSV FORMAT IS CORRECT, IT SHOULD FOLLOW ALL CSVLINT RULES.
    Do not include any other line in the response, just the csv structured data, no acknowledgement nothing your response should be converted to csv file directly.
    



'''    
    messages.append({"role": "user", "content": new_user_input_6}) 
    updated_response_6 = continue_conversation(messages)
    messages.append({"role": "system", "content": updated_response_5})
   
   
    issues_data = updated_response_6.replace('csv', '').replace('', '')

    with open("customer_service_issues107.csv", "+a", encoding='utf-8') as file:
        file.write(issues_data)
    
    print(f'{index} done')
    print(f'{index} done')
    print(f'{index} done')
    print(f'{index} done')
    print(f'{index} done')
    print(f'{index} done')
    print(f'{index} done')
    print(f'{index} done')
    print(f'{index} done')
    print(f'{index} done')
    print(f'{index} done')
    print(f'{index} done')

    print(f'{index} done')

