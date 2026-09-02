from pathlib import Path

import pytest

from workspace import resolve_workspace_path


def test_rejects_paths_outside_workspace():
    root = Path("/tmp/workspace")

    with pytest.raises(ValueError):
        resolve_workspace_path(root, "../outside.txt")

    with pytest.raises(ValueError):
        resolve_workspace_path(root, "/etc/passwd")
