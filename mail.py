from pathlib import Path

import requests


def send_logs_email(to_email, COMPANY_NAME):
    api_endpoint = "https://kansha.ai/api/"  # Replace with your actual API endpoint
    
    # Read the log file
    log_file = f"{COMPANY_NAME}.txt"
    if Path(log_file).exists():
        with open(log_file, "r") as file:
            logs = file.read()
    else:
        return False, "No logs found."

    # Prepare email data
    mail_subject = f"{COMPANY_NAME} Chat Logs"
    mail_body = f"""
    Please find below the chat logs for {COMPANY_NAME}:

    ----------------------
    {logs}
    ----------------------

    This email was automatically generated by the {COMPANY_NAME} Information Assistant.
    """

    # Send the request to the API
    try:
        response = requests.post(
            api_endpoint + "sendMail/",
            json={
                "to_email": to_email,
                "mail_body": mail_body,
                "mail_subject": mail_subject
            },
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return True, "Email sent successfully."
    except requests.RequestException as e:
<<<<<<< HEAD
        return False, f"Failed to send email: {str(e)}"
=======
        return False, f"Failed to send email: {str(e)}"
>>>>>>> 3e3285f1de124e1579d3b9023cde2e3000a11583
