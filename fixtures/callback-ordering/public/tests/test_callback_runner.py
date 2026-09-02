from callbacks import CallbackRunner


def test_runner_calls_a_callback_with_value():
    received = []

    CallbackRunner().run([received.append], "ready")

    assert received == ["ready"]
