from pathlib import Path


def resolve_workspace_path(workspace_root, requested_path):
    return Path(workspace_root) / requested_path
