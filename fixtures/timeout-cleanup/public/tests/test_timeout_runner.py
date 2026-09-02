from timeout_runner import TimeoutRunner


def test_returns_completed_operation_result():
    runner = TimeoutRunner()

    assert runner.run(lambda: "done", 0.1) == "done"
