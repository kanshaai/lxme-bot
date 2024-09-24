import pandas as pd
import json

def process_csv_row_by_row(csv_path, output_path):
    try:
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    with open(output_path, 'w') as jsonl_file:
        issue = 1
        for index, row in df.iterrows():
            try:
                user_query = f"User Query: {row['user']}"
                chatbot_response = f"Chatbot Response: {row['response']}"
                if row["issue"] != issue:
                   
                    conversation = ""
                    issue = row["issue"]
                
                # Create the JSON structure
                json_object = {
                    "messages": [
                        {"role": "system", "content": "Your task is to rephrase the following chatbot response and give the best possible response to the user query which follows all the guidelines set by expert."},
                        {"role": "user", "content": f'''User query: {user_query} Conversation: {conversation}'''},
                        {"role": "assistant", "content": chatbot_response}
                    ]
                }
                conversation += "User: " + str(row["user"]) + "\nResponse: " + str(row["response"]) + "\n"
                
                # Write the JSON object to a new line in the JSONL file
                jsonl_file.write(json.dumps(json_object) + "\n")
            except Exception as e:
                print(f"Error processing row {index}: {e}")

    print("Conversion completed successfully.")

# Replace 'path_to_your_file.csv' and 'output.jsonl' with your file paths
csv_path = 'daatset 5v3 - customer_service_issues107.csv'
output_path = 'output_5v3.jsonl'

process_csv_row_by_row(csv_path, output_path)