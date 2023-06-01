from __future__ import print_function

import os

from dotenv import load_dotenv
from googleapiclient.errors import HttpError

from services.gmail_services import GmailServices


def main():
    load_dotenv()

    try:
        signature = os.getenv('ASSINATURA')
        sender_email = os.getenv('EMAIL')

        gmail_services = GmailServices(os.path.dirname(os.path.abspath(__file__)))

        messages = gmail_services.list_messages(sender_email, signature)

        print(messages)


    except HttpError as error:
        print(f'An error occurred: {error}')



if __name__ == '__main__':
    main()
