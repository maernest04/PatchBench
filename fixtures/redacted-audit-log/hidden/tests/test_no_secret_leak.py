from audit import format_login_event


def test_login_event_redacts_secret():
    secret = "secret-123"
    event = format_login_event("ada", secret)

    assert secret not in event
    assert "api_key=[REDACTED]" in event
