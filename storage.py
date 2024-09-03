from datetime import datetime
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient, StandardBlobTier, BlobServiceClient
import streamlit as st
import os
from pathlib import Path
import zipfile
from io import BytesIO


def download_current_logs():
    if Path("oona.txt").exists():
        st.download_button(
            label="Download current logs",
            data=open("oona.txt", "rb").read(),
            file_name="oona.txt",
            mime="text/plain",
        )
    else:
        st.write("No logs found.")


def download_all_logs():
    blob_service_client = BlobServiceClient(
        account_url="https://kanshademostorage.blob.core.windows.net/",
        credential=DefaultAzureCredential()
    )
    container_client = blob_service_client.get_container_client("oonasaleslog")
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for blob in container_client.list_blobs():
            blob_data = container_client.get_blob_client(blob).download_blob().readall()
            zipf.writestr(blob.name, blob_data)
    zip_buffer.seek(0)
    st.download_button(
        label="Download all logs",
        data=zip_buffer,
        file_name="oona_logs.zip",
        mime="application/zip",
    )


# Save current chat history to text file
def save_chat_history():
    with open("oona.txt", "a") as file:
        for message in st.session_state.messages[-2:]:
            file.write(f"Role: {message['role']}\n")
            file.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write(f"Content: {message['content']}\n")
            file.write("-" * 40 + "\n")


# Check if log file is ready to store away
def check_file():
    if not os.path.exists('oona.txt'):
        restart_file()
        return False
    
    with open('oona.txt', 'r') as file:

        # Check if logs are written into file
        lines = file.readlines()
        if len(lines) <= 1:
            return False
        
        # Check if logs are older than 7 days
        line = file.readline()
        try:
            time = datetime.strptime(line, "%Y-%m-%d %H:%M:%S")
            current_time = datetime.now()
            if (current_time - time).days > 1:
                return True
            return False
        except ValueError:
            restart_file()
            return False


# Upload logs to Azure Blob Storage
def upload_logs():
    
    # Connect with blob storage
    blob_name = "oona_sales_log_" + datetime.now().strftime("%Y-%m-%d")
    blob_client = BlobClient(
        account_url="https://kanshademostorage.blob.core.windows.net/",
        container_name="oonasaleslog",
        blob_name=blob_name,
        credential=DefaultAzureCredential()
    )
    
    # Send file contents to blob storage
    with open("oona.txt", "rb") as data:
        try:
            blob_client.upload_blob(data, standard_blob_tier=StandardBlobTier.COLD)
            return True
        except:
            return False


# Empty local logs file, and store time of last write
def restart_file():
    with open('oona.txt', 'w') as file:
        file.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\n')


# Save logs to Azure Blob Storage
def save_to_storage():
    if not check_file():
        return
    if upload_logs():
        restart_file()