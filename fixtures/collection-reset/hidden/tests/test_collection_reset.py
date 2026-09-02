from event_collection import EventCollection


def test_reset_updates_existing_collection_observers():
    collection = EventCollection()
    observed_items = collection.items
    collection.add({"type": "created"})

    collection.reset()

    assert observed_items == []
    collection.add({"type": "deleted"})
    assert observed_items == [{"type": "deleted"}]
