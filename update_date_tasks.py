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
