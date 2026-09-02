class EventCollection:
    def __init__(self):
        self.items = []

    def add(self, event):
        self.items.append(event)

    def reset(self):
        raise NotImplementedError
