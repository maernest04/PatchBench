class DeliveryService:
    def __init__(self):
        self.events = []

    def deliver(self, message_id, payload):
        raise NotImplementedError
