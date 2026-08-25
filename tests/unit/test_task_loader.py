from pathlib import Path

from patchbench.task_loader import load_task


def test_loads_cache_invalidation_task():
    task = load_task(Path("fixtures/cache-invalidation"))

    assert task.identifier == "cache-invalidation-v1"
    assert task.version == 1
    assert task.dockerfile == Path("fixtures/cache-invalidation/Dockerfile")
    assert task.constraints.cpu_cores == 1.0
    assert [check.visibility for check in task.checks] == ["public", "hidden"]
