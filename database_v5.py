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
        model="gpt-4o-mini",  # Assuming you're using GPT-4o-mini model
        messages=messages
    )
    return response.choices[0].message.content

df = pd.read_csv('customer_service_issues10 - customer_service_issues10.csv')

conversations = df.groupby('issue').apply(
    lambda x: '\n\n'.join([f"User: {row['User']}\nResponse: {row['Response']}" for _, row in x.iterrows()])
).reset_index(name='Conversation')

for index, row in conversations.iterrows():



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


    new_user_input_5 = f'''in above,
    - don't say any annoying phrases like "don't worry" or "I understand"
    - use opportunities where possible to agree with what the user needs or values
    - make user feel you understand them without saying you do. saying is annoying as it feels like a lie
    Important points to remember:
    - Avoid asking for specific transaction details such as amount and recipient's name.
    - Refrain from overusing phrases like "rest assured," "let's work together," and "I understand."
    - Maintain focus on the resolution process without overexplaining or adding unnecessary empathy.
    - Use "swiftly" instead of "ASAP" to give a sense of urgency without being informal.
    - Ensure action steps are realistic and verified to manage user expectations effectively.
    - Remove redundant suggestions that the user may have already checked or clarified.
    - Avoid giving users additional tasks or suggesting they need to provide updates.
    - Keep responses direct and focused, highlighting clear next steps and progress without unnecessary detail.
    - Refrain from hollow empathy that may not seem genuine.
    - Validate and acknowledge the user’s progress or information already provided to move forward efficiently.


    Give your output in such a way that it can be converted to a csv file directly. The format should be like. Add a row issue where issue is {row['issue']}
    issue, user, response
    "issue name","What the hell is going on? I just tried to send money to my friend in the UK, and it says the transaction failed! This is an emergency, and now I'm stuck! Why isn't this working?","I understand your frustration, [User Name]. Let's see what happened with the transaction. Could you please tell me the amount you tried to transfer and the recipient's details?"
    "issue name","It's £500 to [Friend's Name] - [Friend's Account Number]! I can't believe this is happening! I need this money to get to my friend ASAP!","Thank you for that information. I've checked the system, and it seems the transaction was declined due to insufficient funds in your account. We will need to verify the balance before we can process the transfer. Could you confirm the current balance you are seeing in your account?"
    "issue name","Insufficient funds? Are you kidding me? I have more than enough money! I just checked my account, and there's plenty in there! This is ridiculous! What's going on with your system?","I understand your frustration. It appears there might be a temporary glitch in our system causing the balance to be displayed incorrectly. Let me escalate this issue to a human agent who can review your account and the transaction details further. Please hold while I connect you."
    "issue name","Finally, someone who can actually help! I need this sorted out now. This is an emergency.","Good afternoon, [User Name]. My name is [Agent Name]. I understand you're experiencing an issue with an international transfer. I've reviewed your account details and confirmed there are sufficient funds for the transfer. It seems the transaction was stuck due to a temporary system error. I have manually processed the transfer, and it should be completed within the next hour. I apologize for the inconvenience and appreciate your patience."
    "issue name","Thank you, that's a relief. I hope this doesn't happen again. I need to be able to rely on your service, especially in emergencies.","I understand. We are working on improving our system's reliability to prevent these situations in the future. Please let me know if you have any other questions or concerns. Have a good day."
    "issue name","Thank you.",""



    Make sure the csv structure is maintained properly. Since We're using \" for values, make sure they dont appear in messages as they affect the csv format and make it non usuable. Also make sure customer is showing immense emotions and even threats sometimes. IMPORTANT  : MAKE SURE CSV FORMAT IS CORRECT, IT SHOULD FOLLOW ALL CSVLINT RULES.
    Do not include any other line in the response, just the csv structured data, no acknowledgement nothing your response should be converted to csv file directly.
    '''
    messages.append({"role": "user", "content": new_user_input_5})

    updated_response_5 = continue_conversation(messages)
    messages.append({"role": "system", "content": updated_response_5})
    # Print the next response
    #print("Final Output : \n", updated_response_5)
    issues_data = updated_response_5.replace('csv', '').replace('', '')

    with open("customer_service_issues105.csv", "+a", encoding='utf-8') as file:
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

