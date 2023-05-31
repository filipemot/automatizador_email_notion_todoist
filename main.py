from __future__ import print_function

import base64
import os.path
import os
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.modify']



def main():
    load_dotenv()
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        sender_email = os.getenv('EMAIL')
        signature = os.getenv('ASSINATURA')
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q=f'from:{sender_email}').execute()
        messages = results.get('messages', [])

        # Itere sobre os e-mails
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            payload = msg['payload']
            headers = payload['headers']
            parts = payload.get('parts', [])
            message_id = message['id']

            print('Messagem ID:', message_id)

            # Exemplo: imprimir o assunto e o remetente do e-mail
            for header in headers:
                name = header['name']
                value = header['value']
                if name.lower() == 'subject':
                    value = value.replace("Assista a \"", "").replace("\" no YouTube", "")
                    print('Assunto:', value)
                if name.lower() == 'from':
                    print('Remetente:', value)
            # Verificar se há partes no e-mail
            if len(parts) > 0:

                part = parts[0]

                if 'body' in part:
                    data = part['body'].get('data')
                    if data:
                        # Decodificar e imprimir o conteúdo do corpo da mensagem
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        print('Conteúdo:', body.replace("\r\n","").replace(signature, ""))
            #service.users().messages().trash(userId='me', id=message_id).execute()

    except HttpError as error:
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()