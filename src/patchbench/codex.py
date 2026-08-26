import subprocess
from pathlib import Path


class CodexRunError(RuntimeError):
    pass


def run_codex(repository: Path, prompt: str) -> None:
    try:
        result = subprocess.run(
            [
                "codex",
                "exec",
                "--ephemeral",
                "--sandbox",
                "workspace-write",
                "--skip-git-repo-check",
                "-C",
                str(repository),
                prompt,
            ],
            check=False,
        )
    except FileNotFoundError as error:
        raise CodexRunError("Codex CLI is not installed") from error
    if result.returncode != 0:
        raise CodexRunError("Codex did not complete the requested change")
