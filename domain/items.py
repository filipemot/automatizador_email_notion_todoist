from domain.item import Item


class Items:
    def __init__(self, full_sync: bool, list_item: [Item]):
        self.full_sync = full_sync
        self.list_item = list_item
