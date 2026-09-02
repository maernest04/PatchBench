from callbacks import CallbackRunner


def test_runner_preserves_callback_registration_order():
    calls = []

    CallbackRunner().run(
        [lambda value: calls.append(("first", value)), lambda value: calls.append(("second", value))],
        "ready",
    )

    assert calls == [("first", "ready"), ("second", "ready")]
