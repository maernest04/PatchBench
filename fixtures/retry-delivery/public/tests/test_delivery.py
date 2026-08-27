from delivery import DeliveryService


def test_first_delivery_records_an_event():
    service = DeliveryService()

    assert service.deliver("message-1", {"type": "invoice"}) is True
    assert service.events == [{"id": "message-1", "payload": {"type": "invoice"}}]
