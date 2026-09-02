from retry_runner import RetryRunner


def test_waits_with_exponential_backoff_between_retries():
    delays = []
    calls = []

    def operation():
        calls.append("attempt")
        if len(calls) < 3:
            raise ValueError("temporary failure")
        return "sent"

    assert RetryRunner(delays.append).run(operation, 3, 0.25) == "sent"
    assert delays == [0.25, 0.5]
