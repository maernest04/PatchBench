import subprocess
from pathlib import Path

import pytest

from patchbench.working_tree import WorkingTreeError, write_working_tree_patch
from patchbench.workspace import create_candidate_workspace


def test_writes_tracked_and_untracked_changes(monkeypatch, tmp_path):
    repository = tmp_path / "repository"
    repository.mkdir()
    (repository / "new_file.py").write_text("value = 1\n")
    baseline = tmp_path / "baseline"
    baseline.mkdir()
    (baseline / "existing.py").write_text("value = 0\n")
    destination = tmp_path / "candidate.patch"

    def git(command, **kwargs):
        if command[1:3] == ["diff", "--binary"]:
            return subprocess.CompletedProcess(
                command,
                0,
                "diff --git a/existing.py b/existing.py\n--- a/existing.py\n+++ b/existing.py\n@@ -1 +1 @@\n-value = 0\n+value = 1\n",
                "",
            )
        return subprocess.CompletedProcess(command, 0, "new_file.py\0", "")

    monkeypatch.setattr(subprocess, "run", git)

    write_working_tree_patch(repository, destination)

    patch = destination.read_text()
    assert "diff --git a/existing.py b/existing.py" in patch
    assert "--- /dev/null" in patch
    assert "+++ b/new_file.py" in patch
    assert "+value = 1" in patch

    monkeypatch.undo()
    with create_candidate_workspace(baseline, destination) as temporary_directory:
        assert (Path(temporary_directory) / "repository" / "existing.py").read_text() == "value = 1\n"
        assert (Path(temporary_directory) / "repository" / "new_file.py").read_text() == "value = 1\n"


def test_rejects_clean_working_tree(monkeypatch, tmp_path):
    repository = tmp_path / "repository"
    repository.mkdir()

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(command, 0, "", ""),
    )

    with pytest.raises(WorkingTreeError, match="working tree has no changes"):
        write_working_tree_patch(repository, tmp_path / "candidate.patch")
