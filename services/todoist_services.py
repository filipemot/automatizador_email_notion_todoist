from __future__ import annotations

import json
import uuid
from typing import Mapping

import requests

from domain.item import Item
from domain.items import Items


class TodoistServices:
    def __init__(self, token, url):
        self.token = token
        self.url = url

    def create_task(self, title: str, project_id: str, due_date: str) -> None:
        payload = json.dumps(self.__create_data(title, project_id, due_date))
        headers = self.__get_headers()
        self.__execute_request(headers, payload, "created")

    def update_task(self, project_id: str, due_date: str) -> None:
        payload = json.dumps(self.__updated_data(project_id, due_date))
        headers = self.__get_headers()
        self.__execute_request(headers, payload, "updated")

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
    def __create_data(title: str, project_id: str, due_date: str) -> object:
        return {
            'commands': [
                {
                    'type': 'item_add',
                    'temp_id': str(uuid.uuid4()),
                    'uuid': str(uuid.uuid4()),
                    'args': {
                        'content': title,
                        'project_id': int(project_id),
                        "due": {"date": due_date}
                    }
                }
            ]
        }


    @staticmethod
    def __updated_data(project_id, due_date):
        return {
            'commands': [
                {
                    'type': 'item_update',
                    'uuid': str(uuid.uuid4()),
                    'args': {
                        'project_id': int(project_id),
                        "due": {"date": due_date}
                    }
                }
            ]
        }