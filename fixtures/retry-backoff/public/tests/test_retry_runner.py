from retry_runner import RetryRunner


def test_retries_until_operation_succeeds():
    calls = []

    def operation():
        calls.append("attempt")
        if len(calls) == 1:
            raise ValueError("temporary failure")
        return "sent"

    assert RetryRunner(lambda seconds: None).run(operation, 3, 0.1) == "sent"
    assert calls == ["attempt", "attempt"]
