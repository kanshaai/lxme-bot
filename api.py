from flask import Flask, request, jsonify
import pandas as pd
from dotenv import load_dotenv
import os
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Set up the environment keys
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

# Initialize the OpenAI client
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

def continue_conversation(messages):
    response = client.chat.completions.create(
        model="gpt-4o",  # Assuming you're using GPT-4o-mini model
        messages=messages
    )
    return response.choices[0].message.content

@app.route('/rephrase_conversation', methods=['POST'])
def rephrase_conversation():
    data = request.json
    conversation = data.get('conversation')

    if not conversation:
        return jsonify({"error": "No conversation provided"}), 400

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f'''conversation: {conversation}'''}
    ]

    # Add the next prompt for the continuation of the conversation
    user_followup = "what are 5 specific things that if improved in above customer service conversation with a user, would actually help the user be more satisfied"
    messages.append({"role": "user", "content": user_followup})

    # Send the conversation to OpenAI and get the response
    response_content = continue_conversation(messages)
    messages.append({"role": "system", "content": response_content})

    # Rewrite the conversation with improvements
    new_user_input = '''rewrite the entire conversation attached above, again below, after incorporating all above recognised improvements
    and ensure you don't sound disingenous in anyway with the following instruction: Return the actual rephrased version of the conversation, nothing else. Dont mention if it is from a user or customer support agent. Just return the rephrased message. You also dont need to add anything extra in the message. The meaning of the message should be the same as the original message. Do not actually answer any questions asked, just rephrase them.'''
    messages.append({"role": "user", "content": new_user_input})

    updated_response = continue_conversation(messages)
    messages.append({"role": "system", "content": updated_response})

    # Get more improvements
    new_user_input_2 = '''what are 5 specific things that if improved in above customer service conversation with a user, would actually help the user be more satisfied. '''
    messages.append({"role": "user", "content": new_user_input_2})

    updated_response_2 = continue_conversation(messages)
    messages.append({"role": "system", "content": updated_response_2})

    # Rewrite again with new improvements
    new_user_input_3 = '''rewrite the entire conversation attached above, again below, after incorporating all above recognised improvements
    and ensure you don't sound disingenous in anyway. The meaning of the message should be the same as the original message. Do not actually answer any questions asked, just rephrase them.'''
    messages.append({"role": "user", "content": new_user_input_3})

    updated_response_3 = continue_conversation(messages)
    messages.append({"role": "system", "content": updated_response_3})

    # Rate the conversation
    new_user_input_4 = '''rate the above conversation from 1 (criminal) to 10 (unbelievable) basis how Ron Kaufman would rate it'''
    messages.append({"role": "user", "content": new_user_input_4})

    updated_response_4 = continue_conversation(messages)
    messages.append({"role": "system", "content": updated_response_4})

    # Final rewrite with specific instructions
    new_user_input_5 = f'''in above, rewrite the conversation by incorporating this
- don't say any annoying phrases like "don't worry" or "I understand"
- don't over apologise - they're meaningless
- don't make promises a customer support agent cannot keep if the business teams work a certain way
- use opportunities where possible to agree with what the user needs or values
- make user feel you understand them without saying you do. saying is annoying as it feels like a lie
- In any conversation if you have acknowledged user once, don't do it again and again
- user could be lying while frustrated at customer support ---- acknowledge their assessment of their good habits without saying it in a way that makes it seem you have checked their actual records and are putting your stamp of agreement on that assessment. that could get the company in trouble if their actual account activity with the company is not great
- don't say anything that is not needed. If you are not sure, don't say it.
- You dont need to actually answer the question asked by the user. The meaning of the message should be the same as the original message.

*rewrite the entire conversation from above, again below, after incorporating all above recognised improvements
and ensure you don't sound disingenous in anyway*

Return the actual rephrased version of the conversation, nothing else. Dont mention if it is from a user or customer support agent. Just return the rephrased message. You also dont need to add anything extra in the message. The meaning of the message should be the same as the original message. Do not actually answer any questions asked, just rephrase them.
    '''
    messages.append({"role": "user", "content": new_user_input_5})

    final_response = continue_conversation(messages)

    # New addition: Just rephrase using the algorithm without responding to the user
    rephrased_conversation = final_response.strip()

    return jsonify({"rephrased_conversation": rephrased_conversation})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
