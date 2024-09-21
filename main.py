from flask import Flask, request, jsonify, render_template_string
import os
from openai import OpenAI

client = OpenAI()

app = Flask(__name__)

def get_completion(prompt):
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant for axi (axi.com) support."},
        {
            "role": "user",
            "content": prompt
        }
    ])
    return completion.choices[0].message

@app.route("/", methods=['GET'])
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chatbot</title>
    </head>
    <body>
        <h1>Axi Support Agent</h1>
        <h2>Ask about founders, trading platform, products, indices, market</h2>

        <script id="ze-snippet" src="https://static.zdassets.com/ekr/snippet.js?key=86a08f9b-6434-481f-b711-531665878ea4"> </script>
    </body>
    </html>
    ''')

@app.route("/chat", methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get('prompt', '')
    
    if not user_input:
        return jsonify({'error': 'No prompt provided'}), 400
    
    response_text = get_completion(user_input)
    return jsonify({'response': str(response_text.content)})

if __name__ == "__main__":
    app.run(debug=True)
