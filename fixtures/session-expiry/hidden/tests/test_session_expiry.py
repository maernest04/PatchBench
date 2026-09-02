from session_store import SessionStore


def test_expired_session_is_unavailable_at_its_expiry_time():
    store = SessionStore()
    store.create_session("session-1", "user-1", 120)

    assert store.get_session("session-1", 120) is None
    assert "session-1" not in store.sessions
