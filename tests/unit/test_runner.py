import subprocess
from pathlib import Path

import pytest

from patchbench.models import Check, Constraints, Task
from patchbench.runner import DockerRunner, RunnerUnavailableError


def test_reports_unavailable_docker_daemon(monkeypatch):
    task = Task(
        identifier="test",
        version=1,
        root=Path("."),
        repository=Path("."),
        image="python:3.13-slim",
        dockerfile=None,
        constraints=Constraints(timeout_seconds=1, memory_megabytes=64),
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
