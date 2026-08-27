from pathlib import Path

import pytest

from patchbench.task_loader import TaskValidationError, load_task


def test_loads_cache_invalidation_task():
    task = load_task(Path("fixtures/cache-invalidation"))

    assert task.identifier == "cache-invalidation-v1"
    assert task.version == 1
    assert task.dockerfile == Path("fixtures/cache-invalidation/Dockerfile")
    assert task.constraints.cpu_cores == 1.0
    assert [check.visibility for check in task.checks] == ["public", "hidden", "hidden"]
    assert task.checks[-1].kind == "differential"
    assert task.reviewer_ground_truth is not None
    assert task.reviewer_ground_truth.fault_id == "stale-cache-after-delete"
    assert task.reviewer_ground_truth.affected_symbols == ("UserStore.delete_user",)


def test_rejects_malformed_task_contract(tmp_path):
    (tmp_path / "repository").mkdir()
    (tmp_path / "task.yaml").write_text(
        """\
id: malformed
version: 0
repository: repository
runtime:
  image: python:3.13-slim
constraints:
  timeout_seconds: 1
  memory_megabytes: 64
  cpu_cores: 1
checks: []
"""
    )

    with pytest.raises(TaskValidationError, match="version must be a positive integer"):
        load_task(tmp_path)


def test_loads_cli_contract():
    task = load_task(Path("fixtures/cli-report-generation"))
    public_check, hidden_check = task.checks

    assert public_check.kind == "cli"
    assert public_check.command == ("python", "report.py", "Ada Lovelace")
    assert hidden_check.expected_files == (("report.json", '{"name": "Grace Hopper", "slug": "grace-hopper"}\n'),)


def test_loads_api_contract():
    task = load_task(Path("fixtures/api-user-directory"))
    public_check, hidden_check = task.checks

    assert public_check.kind == "pytest"
    assert hidden_check.kind == "api"
    assert hidden_check.expected_stdout.startswith('[{"email":"ada@example.com"')
