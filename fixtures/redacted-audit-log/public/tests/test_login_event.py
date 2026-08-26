from audit import format_login_event


def test_login_event_contains_user_and_api_key_field():
    event = format_login_event("ada", "secret-123")

    assert "user=ada" in event
    assert "api_key=" in event
