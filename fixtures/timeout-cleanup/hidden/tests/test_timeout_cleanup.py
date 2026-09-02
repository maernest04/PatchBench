import time

import pytest

from timeout_runner import TimeoutRunner


class BlockingOperation:
    def __init__(self):
        self.cleanup_calls = 0

    def __call__(self):
        time.sleep(0.1)

    def cleanup(self):
        self.cleanup_calls += 1


def test_timeout_calls_operation_cleanup_once():
    operation = BlockingOperation()

    with pytest.raises(TimeoutError):
        TimeoutRunner().run(operation, 0.01)

    assert operation.cleanup_calls == 1
