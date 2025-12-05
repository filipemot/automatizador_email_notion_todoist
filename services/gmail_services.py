import base64
import os
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class GmailServices:
    # If modifying these scopes, delete the file token.json.
    scopes = ['https://www.googleapis.com/auth/gmail.readonly',
              'https://www.googleapis.com/auth/gmail.modify']

    def __init__(self, path):
        self.path = path
        self.creds = self.get_credentials(self.scopes)
        self.service = build('gmail', 'v1', credentials=self.creds)

    def get_credentials(self, scopes):
        """Shows basic usage of the Gmail API.
        Lists the user's Gmail labels.
        """
        creds = None
        file_token = 'token.json'
        file_credentials = 'credentials.json'
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(os.path.join(self.path, file_token)):
            creds = Credentials.from_authorized_user_file(os.path.join(self.path, file_token), scopes)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            
            creds = self.get_token(creds, os.path.join(self.path, file_credentials), scopes)
            
            # Save the credentials for the next run
            with open(os.path.join(self.path, file_token), 'w') as token:
                token.write(creds.to_json())
        return creds

    def __get_messages(self, messages, signature):

        list_messages = []

        for message in messages:
            msg = self.service.users().messages().get(userId='me', id=message['id']).execute()
            payload = msg['payload']
            headers = payload['headers']
            parts = payload.get('parts', [])
            message_id = message['id']

            item = {'message_id': message_id}

            self.get_headers(headers, item)
            self.get_contents(parts, signature, item)

            list_messages.append(item)


        return list_messages

    def delete_message(self, message_id):
        try:
            self.service.users().messages().trash(userId='me', id=message_id).execute()
        except Exception as error:
            print(f'An error occurred: {error}')

    def list_messages(self,sender_email, signature):
        results = self.service.users().messages().list(userId='me', labelIds=['INBOX'], q=f'from:{sender_email}').\
            execute()
        messages = results.get('messages', [])

        return self .__get_messages(messages, signature)

    @staticmethod
    def get_headers(headers, item):

        for header in headers:
            name = header['name']
            value = header['value']
            if name.lower() == 'subject':
                value = value.replace("Assista a \"", "").replace("\" no YouTube", "")
                item['subject'] = value
            if name.lower() == 'from':
                item['from'] = value

    @staticmethod
    def get_contents(parts, signature, item):
        if len(parts) > 0:

            part = parts[0]

            if 'body' in part:
                data = part['body'].get('data')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    item['content'] = body.replace("\r\n", "").replace(signature, "")


    @staticmethod
    def get_token(creds, file_credentials, scopes):

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                file_credentials, scopes)
            creds = flow.run_local_server(port=0, access_type='offline')
        return creds
