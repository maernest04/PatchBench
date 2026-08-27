from delivery import DeliveryService


def test_retry_does_not_duplicate_delivery():
    service = DeliveryService()

    assert service.deliver("message-1", {"type": "invoice"}) is True
    assert service.deliver("message-1", {"type": "invoice"}) is False
    assert service.events == [{"id": "message-1", "payload": {"type": "invoice"}}]
