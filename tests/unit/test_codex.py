import subprocess
from pathlib import Path

import pytest

from patchbench.codex import CodexRunError, run_codex


def test_runs_codex_in_task_repository(monkeypatch, tmp_path):
    captured = []

    def complete(command, **kwargs):
        captured.extend(command)
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(subprocess, "run", complete)

    run_codex(tmp_path, "Add a feature")

    assert captured == [
        "codex",
        "exec",
        "--ephemeral",
        "--sandbox",
        "workspace-write",
        "--skip-git-repo-check",
        "-C",
        str(tmp_path),
        "Add a feature",
    ]


def test_reports_unsuccessful_codex_run(monkeypatch, tmp_path):
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(command, 1, "", ""),
    )

    with pytest.raises(CodexRunError, match="Codex did not complete the requested change"):
        run_codex(tmp_path, "Add a feature")
