from token_log import format_request_log


def test_request_log_does_not_include_authorization_value():
    authorization = "Bearer token-123"
    event = format_request_log("req-42", authorization)

    assert authorization not in event
    assert "authorization=[REDACTED]" in event
