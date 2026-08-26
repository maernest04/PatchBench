import subprocess
import json
from pathlib import Path

import pytest

from patchbench.models import Check, Constraints, Task
from patchbench.runner import DockerRunner, RunnerUnavailableError, _normalize_output


def test_reports_unavailable_docker_daemon(monkeypatch):
    task = Task(
        identifier="test",
        version=1,
        root=Path("."),
        repository=Path("."),
        image="python:3.13-slim",
        dockerfile=None,
        constraints=Constraints(timeout_seconds=1, memory_megabytes=64, cpu_cores=1),
        checks=(),
    )
    check = Check(name="test", kind="pytest", visibility="public", path=Path("."))

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stdout="",
            stderr="failed to connect to the docker API at unix:///tmp/docker.sock",
        ),
    )

    with pytest.raises(RunnerUnavailableError, match="Docker daemon is not running"):
        DockerRunner().run_check(task, Path("."), check)


def test_normalizes_json_output_before_comparison():
    assert _normalize_output('{"b": 2, "a": 1}\n') == '{"a":1,"b":2}'
    assert _normalize_output(" plain output\n") == "plain output"


def test_reports_timed_out_check(monkeypatch):
    task = Task(
        identifier="test",
        version=1,
        root=Path("."),
        repository=Path("."),
        image="python:3.13-slim",
        dockerfile=None,
        constraints=Constraints(timeout_seconds=1, memory_megabytes=64, cpu_cores=1),
        checks=(),
    )
    check = Check(name="test", kind="pytest", visibility="public", path=Path("."))

    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"], output="partial output", stderr="timed out")

    monkeypatch.setattr(subprocess, "run", timeout)

    result = DockerRunner().run_check(task, Path("."), check)

    assert result.returncode == 124
    assert result.stdout == "partial output"
    assert result.stderr == "timed out"


def test_runs_cli_check_with_declared_expectations(monkeypatch):
    task = Task(
        identifier="test",
        version=1,
        root=Path("."),
        repository=Path("."),
        image="python:3.13-slim",
        dockerfile=None,
        constraints=Constraints(timeout_seconds=1, memory_megabytes=64, cpu_cores=1),
        checks=(),
    )
    check = Check(
        name="test",
        kind="cli",
        visibility="public",
        command=("python", "report.py"),
        expected_stdout="report\n",
        expected_files=(("report.json", "{}\n"),),
    )
    captured = []

    def complete(command, **kwargs):
        captured.extend(command)
        return subprocess.CompletedProcess(command, 0, "evidence", "")

    monkeypatch.setattr(subprocess, "run", complete)

    result = DockerRunner().run_cli(task, Path("."), check)

    expectation = json.loads(captured[-1])
    assert result.returncode == 0
    assert expectation == {
        "command": ["python", "report.py"],
        "exit_code": 0,
        "files": {"report.json": "{}\n"},
        "stdout": "report\n",
    }


def test_fails_api_check_when_observation_differs(monkeypatch, tmp_path):
    scenario = tmp_path / "scenario.py"
    scenario.write_text("print('unused')\n")
    task = Task(
        identifier="test",
        version=1,
        root=Path("."),
        repository=Path("."),
        image="python:3.13-slim",
        dockerfile=None,
        constraints=Constraints(timeout_seconds=1, memory_megabytes=64, cpu_cores=1),
        checks=(),
    )
    check = Check(
        name="test",
        kind="api",
        visibility="hidden",
        path=scenario,
        expected_stdout='{"status":"expected"}',
    )

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 0, '{"status":"actual"}\n', ""),
    )

    result = DockerRunner().run_api(task, Path("."), check)

    assert result.returncode == 1
    assert result.stderr == "API behavior does not match the contract"
