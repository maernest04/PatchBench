import shutil
import subprocess
import tempfile
from pathlib import Path


class PatchValidationError(ValueError):
    pass


class PatchApplicationError(RuntimeError):
    pass


def create_candidate_workspace(repository: Path, patch: Path) -> tempfile.TemporaryDirectory[str]:
    validate_patch(patch)
    temporary_directory = tempfile.TemporaryDirectory(prefix="patchbench-")
    destination = Path(temporary_directory.name) / "repository"
    shutil.copytree(repository, destination)
    result = subprocess.run(
        ["patch", "--batch", "--forward", "-p1", "-i", str(patch.resolve())],
        cwd=destination,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        temporary_directory.cleanup()
        raise PatchApplicationError(result.stderr.strip() or result.stdout.strip() or "patch could not be applied")
    return temporary_directory


def validate_patch(patch: Path) -> None:
    if not patch.is_file():
        raise PatchValidationError(f"patch does not exist: {patch}")

    try:
        lines = patch.read_text().splitlines()
    except OSError as error:
        raise PatchValidationError(f"read patch: {error}") from error

    for line in lines:
        if line.startswith(("--- ", "+++ ")):
            _validate_patch_path(line[4:].split("\t", 1)[0])


def _validate_patch_path(raw_path: str) -> None:
    if raw_path == "/dev/null":
        return
    path = Path(raw_path)
    parts = path.parts[1:] if path.parts and path.parts[0] in {"a", "b"} else path.parts
    if path.is_absolute() or ".." in parts:
        raise PatchValidationError(f"patch contains unsafe path: {raw_path}")
