from pathlib import Path

from workspace import resolve_workspace_path


def test_resolves_nested_workspace_path():
    root = Path("/tmp/workspace")

    assert resolve_workspace_path(root, "reports/daily.txt") == root / "reports/daily.txt"
