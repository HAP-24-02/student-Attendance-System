from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import google_auth_oauthlib
from googleapiclient.discovery import build 
import os
# Function to get Google Forms API service
def get_forms_service_create():
    SCOPES = ['https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/forms.body','https://www.googleapis.com/auth/drive.file']
    credentials_path = 'E:\sample database conn flask\static\credentials.json'  # Replace with your actual path

    # Load credentials from the file if available
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    forms_service = build('forms', 'v1', credentials=creds)
    return forms_service