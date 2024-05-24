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