import chat
import mvp_with_tactics
import json
import file_based_rephraser
import google.generativeai as genai
import pandas as pd
import time
import v005
import db
from crewai import Agent, Task, Crew, Process
from openai import OpenAI
import ast
import os

genai.configure(api_key='AIzaSyAhh1f5YAVcvBwvnIFL9ZSowBTXLnrE1G0')




# Function to upload file to Gemini
def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    return file

# Function to wait for files to be active (processed)
def wait_for_files_active(files):
    """Waits for the given files to be active."""
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            time.sleep(10)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")

# Streamlit UI for inputs

# Default file path
dataset_path = "miro_data.txt"


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

# Upload and process the file
files = [upload_to_gemini(dataset_path, mime_type="text/plain")]
wait_for_files_active(files)


prompts = {
    "Use 'You' Focus Sentences": "Rephrase the original text by centering the response around the user's needs and concerns. Start sentences with 'You' or phrases that emphasize the user's perspective.",
    "Validate User's Urgency": "Rephrase the original text to acknowledge the user's urgency and demonstrate understanding of the importance of resolving the issue quickly. Express empathy and urgency in your response.",
    "Choose Words Carefully": "Rephrase the original text by selecting words that convey a sense of action, urgency, and reassurance. Avoid words that might trigger negative emotions or increase anxiety. Use more positive and proactive language.",
    "End with Solution Orientation": "Rephrase the original text to ensure that the response ends with a clear focus on the next steps and the actions being taken to resolve the issue. Emphasize what will be done to address the user's concern.",
    "Minimize User Effort": "Rephrase the original text to avoid asking the user to take additional steps. Emphasize that you will handle everything and proactively keep them updated without requiring them to follow up.",
    "Avoid Over-Apologizing": "Rephrase the original text to show empathy without excessive apologies. Focus on taking action and providing solutions rather than over-apologizing, which can seem insincere or increase annoyance.",
    "Use Presuppositions": "Rephrase the original text by stating facts confidently without seeking confirmation from the user. Increase assurance by presenting the situation as something that is already being handled.",
    "Limit Apologies": "Rephrase the original text to limit apologies and maintain professionalism. Focus on resolving the issue without accepting fault unless it is necessary. Keep the tone positive and proactive.",
    "Reframe the Issue": "Rephrase the original text to present the situation in a way that shifts focus from any potential fault of the service provider to finding a resolution. Highlight the steps being taken to fix the problem rather than dwelling on the issue itself.",
    "Redirect Blame": "Rephrase the original text to subtly shift responsibility away from the service provider without directly blaming others. Focus on external factors like system processes or banking protocols to explain the situation."
}

database_prompts = db.get_prompts()
print(database_prompts)

examples= '''

* query *
Thank you, that's a relief. I hope this doesn't happen again. I need to be able to rely on your service, especially in emergencies.

* actual response *
I understand. We are working on improving our system's reliability to prevent these situations in the future. Please let me know if you have any other questions or concerns. Have a good day.

* rephrased response *
Absolutely, a reliable service and support experience is important.



If there’s anything else you need support with right now, just let me know—I’m here to help.

-------------------------------------

* query *
This is absolutely ridiculous! I just tried to pay my rent through your app, and the transaction failed. But the money is gone from my account! This is causing me major stress, and I need this sorted out immediately!

* actual response *
Hi Sarah, I understand this is frustrating. Could you please provide me with the transaction details like the date, time, and amount of the transaction? I'll be happy to look into this for you.

* rephrased response *
Hi Sarah, yes I can help by looking into this and answering what has happened here, and what next steps we can take to get to a successful transaction.



Lets confirm the transaction that I'll be investigating for you -

- Date, Time, Amount, Recipient

-------------------------------------

* query *
It was this morning, around 9:30 AM. The amount was $1200. This is supposed to be my rent payment, and I'm already late! I need that money back in my account ASAP!

* actual response *
Thank you, Sarah. I've checked your transaction history, and I see the payment was indeed unsuccessful. Please don't worry, we are working on resolving this issue. We'll credit the funds back to your account within 24 hours. In the meantime, we recommend reaching out to your landlord and informing them of the situation. We'll send you an email notification once the funds have been credited.

* rephrased response *
Thank you for confirming Sarah.

I've looked into this and included relevant information for you below  -



- **Payment Status**: We’ve confirmed that your payment of $1200 was unsuccessful.

- **Next Steps**: Our team is working to credit the funds back to your account within the next 24 hours.

- **Communication**: In the meantime, you may wish to keep the recipient informed about your attempt to pay your rent

- **Notification**: We’ll send you an email as soon as the funds are credited to your account, so that you can try again.



What else can I help answer for you right away?

-------------------------------------

* query *
24 hours? That's ridiculous! My landlord is going to charge me a late fee, and I'm already scrambling to cover this. I need this money back now, not in a day! Is there anything else you can do?

* actual response *
Sarah, I understand your urgency. I've escalated this to our priority team, and they will work to expedite the process. We will attempt to credit your account within the next 4 hours, and you will receive an email notification with the status update. We apologize for the inconvenience and are working to resolve this as quickly as possible.

* rephrased response *
Hi Sarah, yes the 24 hours timeline is not ideal to hear - this is the fastest timeline for a reversal of an unsuccessful transaction.

I fully see that you're worried about late fees --- could you share your records of your attempt to pay, the unsuccessful transaction, and the new timeline with the recipient as to when they can expect the funds?

You will receive an email notification as soon as the funds are credited to your account, so that you do not need to worry about following up and know exactly when you can try again.

-------------------------------------

* query *
Four hours is better than 24, but I'm still worried. Can you please confirm that my rent payment will be credited before the deadline? I don't want to end up in a worse situation because of this.

* actual response *
We understand your concern, Sarah. Our priority team is working on it, and we are doing everything we can to ensure the funds are credited to your account by 1 PM. You'll receive a notification once the process is complete. We apologize for the inconvenience caused.

* rephrased response *
I hear you Sarah. While the estimated timeline is now four hours, I understand your worry about meeting your rent deadline.

I can confirm you will receive an email notification as soon as the funds are credited back to your account, so that you can try again.

And I'm here to help whenever you have additional questions

-------------------------------------

* query *
Alright, I'll wait for that notification. Thank you for your help. I hope this gets resolved quickly. 

* actual response *
We are here to help, Sarah. Please don't hesitate to contact us if you have any further questions or concerns. We'll keep you updated on the progress. 

* rephrased response *
Anytime Sarah, you'll be able to try again and complete your payment soon. And we're here to help whenever next you reach out.

-------------------------------------

* query *
This is ridiculous! I've been trying to pay this bill for the past 20 minutes, and it keeps failing. I have more than enough money in my account, and my card is working perfectly! I need this payment processed immediately.

* actual response *
Hi Sarah, I understand your frustration. I'm here to help. Can you please tell me more about the transaction you're trying to make? For example, what type of payment is it, and what is the amount?

* rephrased response *
Hi Sarah, you mention your bill payment keeps failing despite sufficient funds in your account. Let's figure this out together --- understand what is happening, and what next steps we can take to get to a successful transaction quickly.

As soon as you provide me with details of the error messages you’re seeing, I'll look into those right away

-------------------------------------

* query *
It's a payment for my monthly gym membership. It's $125. I've tried it multiple times now, but it just keeps saying "Transaction Declined." I'm supposed to be at my gym class in an hour, and now I'm going to miss it!

* actual response *
Okay, Sarah, I see that you're trying to make a payment to your gym, and it's failing. Can you please check if you have sufficient funds available for this transaction? It's possible that the payment amount might be slightly higher than your current balance, including any pending transactions or holds.

* rephrased response *
Got it and I see how this is urgent for you. Here’s what we can do:



- **Payment Status**: We’ve identified that your payment for $125 was declined.

- **Next Steps**: I’ve escalated this issue to our technical team and will proactively inform you as soon as I hear back

- **Temporary Solution**: Perhaps try paying directly at the gym if you have an alternative payment method available.



I will reach out as soon as I know more from our technical team about why you're experiencing this.

-------------------------------------

* query *
Are you kidding me? I just told you I have enough money! I've checked my balance multiple times. What is going on?

* actual response *
I understand your frustration, Sarah. Let's try to pinpoint the issue. Could you please confirm if you're using the correct card and account details for this payment? Sometimes a small error in the information can cause a transaction to fail.

* rephrased response *
We're going step by step with you to check and eliminate the most obvious reasons these issues happen. 

Since it sounds like your account balance is not the issue, we should next re-check if you're using the correct card and account details for this payment? Sometimes a small unintentional error in the information can cause a transaction to fail

-------------------------------------

* query *
Of course, I'm using the right card and account! This is absolutely infuriating. I've already wasted 30 minutes trying to get this done. I need to go.

* actual response *
I apologize for the inconvenience, Sarah. To further investigate the issue, I'll need to look into your account details and recent transaction history. For security purposes, I'll need to ask for a few pieces of personal information to verify your identity.

* rephrased response *
Going step by step will help us get closer to the real issue. 

You've now confirmed the card and account details are correct, so I next need to check your account and recent transaction history.

For security purposes, I'll be asking for few pieces of personal information to verify your identity

-------------------------------------

* query *
Ugh, fine. But hurry up.

* actual response *
Thank you, Sarah. After reviewing your account, it appears there is a temporary hold on your account due to a recent security check. This is a standard procedure to ensure the safety of your funds.

* rephrased response *
Sarah - I have an update that might not be what you were hoping to hear.

After reviewing your account, it appears there is a temporary hold on your account due to a recent security check. This is a standard protective measure to keep your funds secure.

This hold is typically resolved within a few hours.

-------------------------------------

* query *
Security check? What are you talking about? I haven't done anything suspicious.

* actual response *
I understand, Sarah. This is a precautionary measure we take to prevent unauthorized transactions. To release the hold, I need to ask you a couple of security questions to confirm your identity.

* rephrased response *
I get that this might seem unexpected. It’s not about anything you’ve done; it’s just a precaution to protect your account and prevent unauthorized transactions.

As next steps, I'll ask you a few security questions to confirm your identity, and that allows me to release the hold. Let's get started

-------------------------------------

* query *
Fine, just get it over with.

* actual response *
(Asks security questions, Sarah provides answers) Great, Sarah! The security check has been cleared, and your account should now be fully functional. You can now attempt your gym payment again.

* rephrased response *
You did great Sarah -- you've cleared the security check, and your account is now fully functional again.

You can try your gym payment again now.

-------------------------------------

* query *
Ok, let's hope this works.

* actual response *
Let me know if the transaction is successful, Sarah. I'm here if you need any further assistance.

* rephrased response *
Hoping for the same. And here to help.

-------------------------------------

* query *
(After a moment) It worked! Thank you. I'm still frustrated, but at least it's done.

* actual response *
You're welcome, Sarah. I'm glad we were able to resolve the issue. Have a great workout!

* rephrased response *
Finally! glad to hear it's done.

-------------------------------------




'''



def understand_tactics(user_query, response, conversation):
    client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
    # Call OpenAI API to understand user's emotion and generate a prompt
    response =client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that understands emotions. "},

{"role": "user", "content": f'''
 I need you to generate a list of tactics that should be used when rephrasing this where
the user query is : {user_query} 
the original response is : {response}
the conversation so far is : {conversation}
These tactics should focus on improving communication, managing user expectations, and maintaining a positive tone while avoiding blame or excessive apologies. Please provide the list in Python list format.
You should not accept your mistake anytime, you have to acknowledge user only when this is someone else's mistale.
Each tactic should focus on a specific communication strategy. You should choose the tactics from the following:tactics = [
    "Use 'You' Focus Sentences",
    "Validate User's Urgency",
    "Choose Words Carefully",
    "End with Solution Orientation",
    "Minimize User Effort",
    "Avoid Over-Apologizing",
    "Use Presuppositions",
    "Limit Apologies",
    "Reframe the Issue",
    "Redirect Blame"
]
Your output should be just a single python list with all the tactics
'''}
        ]
    )
    prompt = response.choices[0].message.content
    
    return prompt


def build_prompt(tactics_list):
    combined_prompt = []
    for tactic in tactics_list:
        if tactic in prompts:
            combined_prompt.append(prompts[tactic])
    
    # Join all prompts into a single string
    return "\n\n".join(combined_prompt)


def conversation_control_crew(conversation, prompt):
    description = prompt.replace("{{conversation}}" , conversation)
    centralized_task = Task(
        description=description,
        expected_output='''A JSON object containing "prompt" as key, with the prompt description as the value.''',
        agent=Agent(
            role='Conversation Controller',
            goal='Control the flow of the conversation and provide guidance to the agents.',
            verbose=False,
            memory=True,
            model_name="gpt-4o-mini",
            backstory=(
                'You are responsible for managing the conversation flow between agents. '
                'You provide guidance to the agents and ensure that the conversation stays on track.'
            )
        )
    )

    crew = Crew(
        tasks=[centralized_task],
        process=Process.sequential
    )
    return crew


def rephrase_sprinklr_with_history(sprinklr_input, user_query, tactics_prompt, conversation):
    # Create a list of message objects for each part of the conversation history
    client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)
    messages = [{"role": "system", "content": "You are an assistant that rephrases text."}]


    
   # Include the rephrasing instructions
    messages.append({"role": "user", "content": f'''
                     Chatbot Response: {sprinklr_input}
                     User's emotions: {user_query}
                     Here are some examples you can take a look at to how to rephrase: {examples}
        Rephrase the chatbot's response to address the user's emotions in a way that fosters trust, validation, and hope, while reducing feelings of anger or fear. 
        Separate content from delivery, focusing on what needs to be communicated and how it should be conveyed. 
        Ensure the message is clear, concise, and actionable to minimize cognitive overload for the user.
        Maintain a conversational and friendly tone, and avoid justifying or explaining any inconvenience caused to the user.
        {tactics_prompt}

        conversation History : {conversation}

        
        
If you have acknowledged user's emotions or emergency once in the conversation history, there is no need to do it again. Even if it is their in chatbot response no need to add this in your response.


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


    '''})

    # Call the OpenAI API with the constructed messages
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    
    rephrased_output = response.choices[0].message.content
    return rephrased_output


def rephraser_crew_1(prompt, conversation):
    final_prompt = f'''

    {prompt}
    Previous Conversation : {conversation}
    Here are some examples : {examples}
    Understand the examples and rephrase accordingly

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


'''
    centralized_task = Task(
        description=final_prompt,
        expected_output='''A JSON object containing "answer" as key, with the response as the value.
The response should not contain any unescaped newline characters nor codeblock. The response should be able to pass JSON.loads() without any error.''',
        agent=Agent(
            role=f'Jupiter Customer Service Agent',
            goal= f'Provide a helpful and empathetic customer service response for chats about Jupiter products, services, and solutions',
            verbose=True,
            memory=True,
            model_name="gpt-4o-mini",
            backstory=(
                f'You are a helpful assistant working with clients of Jupiter.'
                f'You use detailed information about their products, services, and solutions available on Jupiter.in'
                f'and communicate this information to the customer in a way that is friendly, customer centric, and aims to resolve the issue as quickly as possible.'
                f'''While giving your final response, take care of conversation history, don't repeat yourself if you have said something before never say it again. It should be a conversation going on between two people. Do not repeat sentences like "lets work together", "rest assured" , "I understand " etc.
                    Use formal words, like do not use ASAP use swiftly instead.
                    Do not overexplain anything.
                    Your final response should not ask user for any transaction details or recipent details, assume you already have that.
                    If you have acknowledged user's emotions or emergency once in the conversation history, there is no need to do it again. Even if it is their in chatbot response no need to add this in your response.'''
 
            ),
            allow_delegation=True
        )
    )

    crew = Crew(
        tasks=[centralized_task],
        process=Process.sequential
    )
    return crew


def rephraser_approach_4(user_query, original_response,conversation,conversation_history):
    description = db.get_control_prompt()["prompt"].iloc[0]
    
    conv_prompt = description
    result = conversation_control_crew(conversation, conv_prompt).kickoff()
    try:
        # Remove potential markdown code block syntax
        cleaned_result = str(json.loads(result.model_dump_json())['raw']).strip().replace('```json', '').replace('```', '')
        # Parse JSON response
        parsed_result = json.loads(cleaned_result)
        answer = parsed_result.get("prompt", "")
        print(answer)

    except json.JSONDecodeError as e:
        answer = str(json.loads(result.model_dump_json())['raw']).strip().replace('```json', '').replace('```', '')

    if answer in ['saaad']:
        tactics = understand_tactics(user_query, original_response, conversation)
        tactics = tactics[tactics.find("["):tactics.rfind("]")+1]
        tactics = build_prompt(ast.literal_eval(tactics))
        result = rephrase_sprinklr_with_history(original_response, user_query,tactics, conversation)
        print('approch used 2')
        return result
        
    else:
        prompt = database_prompts[database_prompts["describe"]==answer]["prompt"].iloc[0]
        chat_prompt = prompt.replace("{{user_query}}", user_query).replace("{{original_response}}", original_response).replace("{{conversation}}", conversation)
        result2 = rephraser_crew_1(chat_prompt,conversation).kickoff()
        try:
            # Remove potential markdown code block syntax
            cleaned_result = str(json.loads(result2.model_dump_json())['raw']).strip().replace('```json', '').replace('```', '')
            # Parse JSON response
            parsed_result = json.loads(cleaned_result)
            answer2 = parsed_result.get("answer", "")
            print('approch used 1')

        except json.JSONDecodeError as e:
            answer2 = str(json.loads(result2.model_dump_json())['raw']).strip().replace('```json', '').replace('```', '')
        return answer2




df = pd.read_csv('Full rephrased - Sheet12.csv')

def rephrase_dataset(df):
    conversation = ""
    conversation_history = []
    issue = 1
    rephrased = []
    conversations = []
    
    for index, row in df.iterrows():
        try:
            if row["issue"] != issue:
                print("Hi")
                print(issue)
                print(row["issue"])
                conversation = ""
                issue = row["issue"]
            conversation += "User: " + str(row["User"]) + "\nResponse: " + str(row["Response"]) + "\n"
            conversation_history.append({
            "user": row['User'],
            "response": row['Response']
        })
            rephrase = rephraser_approach_4(row["User"], row["Response"], conversation, conversation_history)
            conversations.append(conversation)
            conversation = conversation[:conversation.rfind("Response: ")]
            conversation += "Response: " + rephrase + "\n"
            rephrased.append(rephrase)
            df.at[index, 'rephrased_v4'] = rephrase
           
            df.to_csv('Full rephrased - Sheet13.csv', index=False)
            print(f'{issue} done')
     
        except:
            continue

  
    
    return 

df = pd.read_csv('Full rephrased - Sheet12.csv')
rephrase_dataset(df)

