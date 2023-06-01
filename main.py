from __future__ import print_function

import os

from dotenv import load_dotenv
from googleapiclient.errors import HttpError

from services.gmail_services import GmailServices
from services.notion_services import NotionServices


def main():
    load_dotenv()

    try:
        signature = os.getenv('ASSINATURA')
        sender_email = os.getenv('EMAIL')
        notion_url = os.getenv('NOTION_API_URL')
        notion_token = os.getenv('NOTION_TOKEN')
        notion_database_id = os.getenv('NOTION_DATABASE')

        gmail_services = GmailServices(os.path.dirname(os.path.abspath(__file__)))
        messages = gmail_services.list_messages(sender_email, signature)

        notion_services = NotionServices(notion_token, notion_url)

        for message in messages:
            notion_services.create_task(notion_database_id, message['assunto'], message['conteudo'])


    except HttpError as error:
        print(f'An error occurred: {error}')



if __name__ == '__main__':
    main()
