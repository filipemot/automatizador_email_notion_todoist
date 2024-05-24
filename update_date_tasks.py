import os
from datetime import datetime, timedelta

from dotenv import load_dotenv

from domain.item_update import ItemUpdate
from services.todoist_services import TodoistServices


def is_not_expire_task(due_date_task: datetime) -> bool:
    if due_date_task > datetime.now() + timedelta(days=1):
        return True

    return False


def main():
    load_dotenv()
    todoist_project = os.getenv('TODOIST_PROJECT_UPDATED_DATE')

    projects = todoist_project.split(',')

    todoist_url = os.getenv('TODOIST_API_URL')
    todoist_token = os.getenv('TODOIST_TOKEN')
    todoist_services = TodoistServices(todoist_token, todoist_url)

    items = todoist_services.get_tasks()

    item_updated = []
    for item in items.list_item:
        if item.project_id in projects and item.due_date is not None:
            due_date_task = datetime.fromisoformat(item.due_date.split('T')[0])

            if is_not_expire_task(due_date_task):
                continue

            due_date = (due_date_task + timedelta(days=90)).replace(hour=15, minute=0, second=0).isoformat()

            item_updated.append(ItemUpdate(item.id_item, due_date))

    todoist_services.update_task(item_updated)


if __name__ == '__main__':
    main()
