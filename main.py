from flask import Flask, request, jsonify, render_template_string
import os
import google.generativeai as genai

# Configure the Gemini API
genai.configure(api_key='AIzaSyDTtlEtTf3fEUxXYyOU1-n_a2EZ8cNh6yc')

# Set up generation configuration for Gemini
generation_config = {
    "temperature": 0.2,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Create the model session
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
)

app = Flask(__name__)

def get_completion(prompt):
    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": ["You are a helpful assistant for axi (axi.com) support."],
            },
            {
                "role": "model",
                "parts": ["Okay, I'm ready to assist! How can I help you today?"],
            },
        ]
    )
    
    # Send the user input to the Gemini model
    response = chat_session.send_message(prompt)
    
    return response.text

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
    
    # Get the response from the Gemini model
    response_text = get_completion(user_input)
    
    return jsonify({'response': response_text})

if __name__ == "__main__":
    app.run(debug=True)
