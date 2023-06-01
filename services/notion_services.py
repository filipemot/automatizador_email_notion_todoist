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
            print("Tarefa criada com sucesso!")
        else:
            print("Erro ao criar a tarefa:", response.status_code, response.text)

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