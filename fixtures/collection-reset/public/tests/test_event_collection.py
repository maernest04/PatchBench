from event_collection import EventCollection


def test_reset_clears_recorded_events():
    collection = EventCollection()
    collection.add({"type": "created"})

    collection.reset()

    assert collection.items == []
