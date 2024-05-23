class Item:
    def __init__(self, project_id: str, id_item: str, due_date: str, is_recurring: bool, content: str):
        self.project_id = project_id
        self.id_item = id_item
        self.due_date = due_date
        self.is_recurring = is_recurring
        self.content = content
