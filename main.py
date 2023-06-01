from __future__ import print_function

import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from googleapiclient.errors import HttpError

from services.gmail_services import GmailServices
from services.notion_services import NotionServices
from services.todoist_services import TodoistServices


def main():
    load_dotenv()

    try:
        signature = os.getenv('ASSINATURA')
        sender_email = os.getenv('EMAIL')
        notion_url = os.getenv('NOTION_API_URL')
        notion_token = os.getenv('NOTION_TOKEN')
        notion_database_id = os.getenv('NOTION_DATABASE')
        todoist_url = os.getenv('TODOIST_API_URL')
        todoist_token = os.getenv('TODOIST_TOKEN')
        todoist_project = os.getenv('TODOIST_PROJECT')

        gmail_services = GmailServices(os.path.dirname(os.path.abspath(__file__)))
        messages = gmail_services.list_messages(sender_email, signature)

        notion_services = NotionServices(notion_token, notion_url)

        todoist_services = TodoistServices(todoist_token, todoist_url)
        due_date = (datetime.now() + timedelta(days=25)).replace(hour=10, minute=0, second=0).isoformat()

        for message in messages:
            notion_services.create_task(notion_database_id, message['subject'], message['content'])
            todoist_services.create_task(message['subject'], todoist_project, due_date)
            gmail_services.delete_message(message['message_id'])



    except HttpError as error:
        print(f'An error occurred: {error}')



if __name__ == '__main__':
    main()
