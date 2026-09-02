from session_store import SessionStore


def test_active_session_is_returned():
    store = SessionStore()
    store.create_session("session-1", "user-1", 120)

    assert store.get_session("session-1", 119) == {
        "id": "session-1",
        "user_id": "user-1",
        "expires_at": 120,
    }
