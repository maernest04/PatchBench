from user_store import UserStore


def test_repeated_reads_use_the_cache():
    store = UserStore()
    store.create_user(42, "Ada")

    assert store.get_user(42) == {"id": 42, "name": "Ada"}
    assert store.get_user(42) == {"id": 42, "name": "Ada"}
    assert store.database_reads == 1
