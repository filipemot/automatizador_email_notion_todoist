import json

import requests


class TodoistServices:
    def __init__(self, token, url):
        self.token = token
        self.url = url

    def create_task(self, title, project_id, due_date):
        data = self.create_data(title, project_id, due_date)
        headers = self.get_headers()

        response = requests.post(self.url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            print("TodoIst - Task created successfully!")
        else:
            print("TodoIst - Error creating task:", response.status_code, response.text)


    def get_headers(self):
        return {
            "Authorization": "Bearer " + self.token,
            "Content-Type": "application/json"
        }

    @staticmethod
    def create_data(title, project_id, due_date):
        return {
            "content": title,
            "due_date": due_date,
            "project_id": project_id
        }

