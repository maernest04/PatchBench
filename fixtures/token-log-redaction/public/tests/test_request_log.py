from token_log import format_request_log


def test_request_log_contains_request_and_authorization_field():
    event = format_request_log("req-42", "Bearer token-123")

    assert "id=req-42" in event
    assert "authorization=" in event
