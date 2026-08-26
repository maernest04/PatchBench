import difflib
import subprocess
from pathlib import Path


class WorkingTreeError(RuntimeError):
    pass


def write_working_tree_patch(repository: Path, destination: Path) -> None:
    diff = _git(repository, ["diff", "--binary", "HEAD"])
    untracked = _git(repository, ["ls-files", "--others", "--exclude-standard", "-z"])
    for relative_path in filter(None, untracked.split("\0")):
        path = repository / relative_path
        if not path.is_file():
            continue
        diff += "".join(
            difflib.unified_diff(
                [],
                path.read_text().splitlines(keepends=True),
                fromfile="/dev/null",
                tofile=f"b/{relative_path}",
            )
        )
    if not diff:
        raise WorkingTreeError("working tree has no changes")
    destination.write_text(diff)


def _git(repository: Path, arguments: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *arguments],
            cwd=repository,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as error:
        raise WorkingTreeError("Git is not installed") from error
    if result.returncode != 0:
        raise WorkingTreeError(result.stderr.strip() or "could not read working tree changes")
    return result.stdout
