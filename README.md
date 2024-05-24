# Automatizador de Leitura de Emails e Integração no Notion e TodoIst

# Objetivo
- Ler os emails de uma caixa de entrada
- Filtrar os emails por remetente
- Criar uma tarefa no TodoIst
- Criar uma página no Notion
- Script auxiliar para atualizar a data das tarefas vencidas

# Instalar

- pip install python-dotenv
- pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Configurar API GMAIL

- Entrar em https://console.cloud.google.com/
- Criar um Projeto caso não exista
- Entrar no projeto
- Ir em APIs e Serviços(https://console.cloud.google.com/apis/library)
- Ativar a API do Gmail
- Ir em Credenciais(https://console.cloud.google.com/apis/credentials)
- Criar Credenciais de OAuth2, para computador
- Adicionar scope de APIS do GmailAPI
- Gravar arquivo de Credenciais no formato JSON
- A primeira vez que rodar o script, será necessário autorizar o acesso a conta do Gmail
- O script irá gerar um arquivo token.json, que será utilizado para autorizar o acesso a conta do Gmail

# Exemplo do arquivo credentials

```json
{
	"installed": {
		"client_id": "ClientID do OAuth2",
		"project_id": "Nome do Projeto",
		"auth_uri": "https://accounts.google.com/o/oauth2/auth",
		"token_uri": "https://oauth2.googleapis.com/token",
		"auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
		"client_secret": "ClientSecret do OAuth2",
		"redirect_uris": ["http://localhost"]
	}
}
```

# Arquivo de .env

Crie um arquivo .env na raiz do projeto com as seguintes variáveis:

```
EMAIL=Email que será filtrado na caixa de entrada
ASSINATURA=Assinatura que será removida do corpo do email
```

# Configurar Notion

- Criar uma integração no Notion(https://www.notion.com/my-integrations)
- Clicar em nova Integração
- Selecionar qual a workspace que será integrada
- Definir um nome para a integração
- Copie o token de integração
- Adicione ele no .env com o nome NOTION_TOKEN
- Vai na Workspace do Notion
- Crie uma página
- Adicione um Database
- Adicione as propriedades que desejar
- Clique nos 3 pontinhos do Database
- Adicione a conexão com a Integração
- Clique em share e copie o link da página. Exemplo: https://www.notion.so/1212. O Id seria o 1212
- Adicione o Id da página no .env com o nome NOTION_DATABASE_ID

# Configurar TodoIst
- Crie em .env a variável TODOIST_API_URL=https://api.todoist.com/sync/v9/sync
- Pegue o token de integração https://todoist.com/app/settings/integrations/developer
- Adicione ele no .env com o nome TODOIST_TOKEN
- Pegue o Id do projeto que deseja adicionar as tarefas
- Adicione ele no .env com o nome TODOIST_PROJECT
- Versão da API utlizada v9

# Configurar o script .env

```env
EMAIL=Email que será filtrado na caixa de entrada
ASSINATURA=Assinatura que será removida do corpo do email
NOTION_API_URL=https://api.notion.com/v1/pages
NOTION_TOKEN=Token de integração do Notion
NOTION_DATABASE_ID=Id da página do Notion
TODOIST_API_URL=https://api.todoist.com/sync/v9/sync
TODOIST_TOKEN=Token de integração do TodoIst
TODOIST_PROJECT=Id do projeto do TodoIst
TODOIST_PROJECT_UPDATED_DATE=Projetos que serão atualizados a data, caso as tarefas já estiverem vencidas Ex: 2263788238,2263786127
```

# Executar o script - Integração Gmail, Notion e TodoIst

```bash
python main.py
```

# Executar o script - Atualizar a data das tarefas vencidas

```bash
python update_date_tasks.py
```


# Classes


## Gmail

- Classe responsável por fazer a conexão com o Gmail
- Faz a leitura dos emails
- Faz a filtragem dos emails
- Faz a remoção da assinatura do email
- Retorna o email filtrado e sem assinatura

- Métodos
  - get_credentials - Retorna as credenciais do Gmail
  - list_messages - Retorna os emails filtrados
  - delete_message - Deleta o email da caixa de entrada  


```python
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
        self.service.users().messages().trash(userId='me', id=message_id).execute()

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
            creds = flow.run_local_server(port=0)
        return creds
```

## Notion

- Classe responsável por fazer a conexão com o Notion
- Faz a criação da task no Notion

- Métodos
  - create_task - Cria a task no Notion

```python   
import json

import requests


class NotionServices:
    def __init__(self, token, url):
        self.token = token
        self.url = url

    def create_task(self, database_id, title, contents):
        data = self.create_data(database_id, title, contents)
        headers = self.get_headers()

        response = requests.post(self.url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            print("Notion - Task created successfully!")
        else:
            print("Notion - Error creating task:", response.status_code, response.text)

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2021-05-13"
        }

    def create_data(self, database_id, title, contents):
        return {
            "parent": {
                "database_id": database_id
            },
            "properties": {
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]

            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": contents
                                }
                            }
                        ]
                    }
                }
            ]
        }
```

# Todoist

- Classe responsável por fazer a conexão com o Todoist
- Faz a criação da task no Todoist
- Métodos
  - create_task - Cria a task no Todoist
  - update_task - Atualiza a task no Todoist
  - get_tasks - Retorna as tasks do Todoist

```python
from __future__ import annotations

import json
import uuid
from typing import Mapping

import requests

from domain.item import Item
from domain.item_create import ItemCreate
from domain.item_update import ItemUpdate
from domain.items import Items


class TodoistServices:
    def __init__(self, token, url):
        self.token = token
        self.url = url

    def create_task(self, items_created: [ItemCreate]) -> None:
        list_split = self.__split_list_in_length_100(items_created)

        for items in list_split:
            payload = json.dumps(self.__create_data(items))
            headers = self.__get_headers()
            self.__execute_request(headers, payload, "created")

    def update_task(self, items_updated: [ItemUpdate]) -> None:

        list_split = self.__split_list_in_length_100(items_updated)

        for items in list_split:
            payload = json.dumps(self.__updated_data(items))
            headers = self.__get_headers()
            self.__execute_request(headers, payload, "updated")

    @staticmethod
    def __split_list_in_length_100(items: [ItemUpdate]) -> [[ItemUpdate]]:
        return [items[i:i + 100] for i in range(0, len(items), 100)]

    def get_tasks(self) -> Items:
        headers = self.__get_headers()
        payload = json.dumps({
            "sync_token": "*",
            "resource_types": [
                "items"
            ]
        })
        response = requests.request("POST", self.url, headers=headers, data=payload)

        return self.__convert_response_to_items(response)

    @staticmethod
    def __convert_response_to_items(response: any) -> Items:
        json_response = response.json()

        items = []
        for item in json_response['items']:

            due_date = None
            due_is_recurring = False

            if item['due'] is not None:
                due_date = item['due']['date']
                due_is_recurring = item['due']['is_recurring']

            items.append(Item(
                item['project_id'],
                item['id'],
                due_date,
                due_is_recurring,
                item['content']
            ))
        item = Items(json_response['full_sync'], items)

        return item


    def __execute_request(self, headers: Mapping[str, str | bytes], payload, message) -> None:
        response = requests.post(self.url, headers=headers, data=payload)
        if response.status_code == 200:
            print(f"TodoIst - Task {message} successfully!")
        else:
            print("TodoIst - Error creating task:", response.status_code, response.text)

    def __get_headers(self) -> Mapping[str, str | bytes]:
        return {
            "Authorization": "Bearer " + self.token,
            "Content-Type": "application/json"
        }

    @staticmethod
    def __create_data(items_created) -> object:
        commands = {'commands': []}

        for item in items_created:
            commands['commands'].append({
                'type': 'item_add',
                'temp_id': str(uuid.uuid4()),
                'uuid': str(uuid.uuid4()),
                'args': {
                    'content': item.title,
                    'project_id': int(item.project_id),
                    "due": {"date": item.due_date}
                }
            })

        return commands


    @staticmethod
    def __updated_data(items_updated: [ItemUpdate]) -> object:
        commands = {'commands': []}

        for item in items_updated:
            commands['commands'].append({
                'type': 'item_update',
                'uuid': str(uuid.uuid4()),
                'args': {
                    'id': item.item_id,
                    "due": {"date": item.due_date}
                }
            })


        return commands
```

```python
from domain.item import Item


class Items:
    def __init__(self, full_sync: bool, list_item: [Item]):
        self.full_sync = full_sync
        self.list_item = list_item
```

```python
class Item:
    def __init__(self, project_id: str, id_item: str, due_date: str, is_recurring: bool, content: str):
        self.project_id = project_id
        self.id_item = id_item
        self.due_date = due_date
        self.is_recurring = is_recurring
        self.content = content
```

```python
class ItemUpdate:
    def __init__(self, item_id: int, due_date: str):
        self.item_id = item_id
        self.due_date = due_date
```

# Main

```python
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
```

# update_date_tasks

```python
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv

from services.todoist_services import TodoistServices


def main():
    load_dotenv()
    todoist_project = os.getenv('TODOIST_PROJECT_UPDATED_DATE')

    projects = todoist_project.split(',')

    todoist_url = os.getenv('TODOIST_API_URL')
    todoist_token = os.getenv('TODOIST_TOKEN')
    todoist_services = TodoistServices(todoist_token, todoist_url)

    items = todoist_services.get_tasks()

    for item in items.list_item:
        if item.project_id in projects and item.due_date is not None:
            due_date_now = datetime.fromisoformat(item.due_date)

            if due_date_now > datetime.now() + timedelta(days=1):
                continue

            due_date = (due_date_now + timedelta(days=90)).replace(hour=15, minute=0, second=0).isoformat()

            todoist_services.update_task(item.id_item, due_date)


if __name__ == '__main__':
    main()

```


# Github

https://github.com/filipemot/automatizador_email_notion_todoist