import os
import subprocess
import sys
from pathlib import Path

import pytest

from patchbench.workspace import create_candidate_workspace


@pytest.mark.parametrize(
    ("patch_name", "hidden_returncode"),
    [("correct.patch", 0), ("stale-cache.patch", 1)],
)
def test_fixture_separates_visible_and_hidden_behavior(patch_name, hidden_returncode):
    fixture = Path("fixtures/cache-invalidation").resolve()
    environment = os.environ | {"PYTHONPATH": ""}

    with create_candidate_workspace(fixture / "repository", fixture / "candidates" / patch_name) as temporary_directory:
        workspace = Path(temporary_directory) / "repository"
        environment["PYTHONPATH"] = str(workspace)
        public = subprocess.run(
            [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", str(fixture / "public" / "tests")],
            cwd=workspace,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        hidden = subprocess.run(
            [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", str(fixture / "hidden" / "tests")],
            cwd=workspace,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

    assert public.returncode == 0, public.stdout + public.stderr
    assert hidden.returncode == hidden_returncode, hidden.stdout + hidden.stderr


def test_candidate_workspace_is_cleaned_up():
    fixture = Path("fixtures/cache-invalidation").resolve()
    with create_candidate_workspace(fixture / "repository", fixture / "candidates" / "correct.patch") as temporary_directory:
        workspace_root = Path(temporary_directory)
        assert workspace_root.is_dir()

    assert not workspace_root.exists()
