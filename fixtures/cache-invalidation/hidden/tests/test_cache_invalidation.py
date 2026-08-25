from user_store import UserStore


def test_deleted_user_is_not_returned_from_cache():
    store = UserStore()
    store.create_user(42, "Ada")

    assert store.get_user(42) == {"id": 42, "name": "Ada"}
    assert store.delete_user(42) is True
    assert store.get_user(42) is None
