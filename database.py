import chat
import mvp_with_tactics
import json
import file_based_rephraser
import google.generativeai as genai
import pandas as pd
import time

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


df = pd.read_csv('Untitled spreadsheet - Sheet1 (1).csv')

response1_list = []
response2_list = []
i = 1
for index, row in df.iterrows():
    try:
        if row['User']:


            user_query = row['User']

            original_response = row['Response']

            chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        files[0],
                        "Understand the manner in which we rephrase the response from the file shared and your job is to rephrase the new queries given to you.",
                    ],
                },
                {
                    "role": "model",
                    "parts": [
                        "Okay, I understand. You want me to rephrase responses to customer queries based on the pattern you've shown in the `dataset.txt` file. I will not mention names until specified in query or actual response.",
                    ],
                },
            ]
        )
            response3 = chat_session.send_message(f"query: {user_query}\n\nresponse: {original_response}\n\nJust send back the rephrased response.")
        


            result2 = chat.conversation_control_crew(original_response).kickoff()

            try:
                # Remove potential markdown code block syntax
                cleaned_result = str(json.loads(result2.model_dump_json())['raw']).strip().replace('```json', '').replace('```', '')
                print(json.loads(result2.model_dump_json())['raw'])
                # Parse JSON response
                parsed_result = json.loads(cleaned_result)
                answer2 = parsed_result.get("prompt", "")
                print(answer2)
            

            except json.JSONDecodeError as e:
                print(e)
                #st.markdown(f"**Error parsing JSON:**\n{result2}")
                answer2 = str(json.loads(result2.model_dump_json())['raw']).strip().replace('```json', '').replace('```', '')



            prompts = chat.db.get_prompts()

            try:
                prompt = prompts[prompts["describe"]==answer2]["prompt"].iloc[0]
            except:
                print('error')
            updated_prompt = prompt.replace("{{user_query}}", user_query).replace("{{original_response}}", original_response).replace("{{conversation}}"," ")
            result3 = chat.rephraser_crew(updated_prompt).kickoff()
            

            try:
                # Remove potential markdown code block syntax
                cleaned_result = str(json.loads(result3.model_dump_json())['raw']).strip().replace('```json', '').replace('```', '')
                print(json.loads(result2.model_dump_json())['raw'])
                # Parse JSON response
                parsed_result = json.loads(cleaned_result)
                answer3 = parsed_result.get("answer", "")
                

            except json.JSONDecodeError as e:
                print(e)
                #st.markdown(f"**Error parsing JSON:**\n{result2}")
                answer3 = str(json.loads(result3.model_dump_json())['raw']).strip().replace('```json', '').replace('```', '')






            user_emotions = mvp_with_tactics.understand_tactics(user_query, original_response )
            tactic_prompt = mvp_with_tactics.generate_prompt(user_emotions)
            response2 = mvp_with_tactics.rephrase_sprinklr(original_response, user_query, tactic_prompt)
            response1_list.append(answer3)
            response2_list.append(response2)
            print(f'{i} done')
            i = i+1
            df.at[index, 'response1'] = answer3
            df.at[index, 'response2'] = response2
            df.at[index, 'response3'] = response3.text
            # Step 4: Save the updated DataFrame back to the CSV file
            df.to_csv('updated_indifi.csv', index=False)
    
    except:
        continue




