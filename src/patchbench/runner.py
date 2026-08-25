import subprocess
import time
from pathlib import Path

from patchbench.models import Check, CommandResult, Task


class RunnerUnavailableError(RuntimeError):
    pass


class DockerRunner:
    def __init__(self):
        self._prepared_images: set[str] = set()

    def run_check(self, task: Task, workspace: Path, check: Check) -> CommandResult:
        self._ensure_image(task)
        command = [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "--read-only",
            "--tmpfs",
            "/tmp",
            "--memory",
            f"{task.constraints.memory_megabytes}m",
            "--pids-limit",
            "256",
            "--mount",
            f"type=bind,source={workspace.resolve()},target=/workspace,readonly",
            "--mount",
            f"type=bind,source={check.path.resolve()},target=/checks,readonly",
            "--workdir",
            "/workspace",
            "--env",
            "PYTHONDONTWRITEBYTECODE=1",
            "--env",
            "PYTHONPATH=/workspace",
            task.image,
            "python",
            "-m",
            "pytest",
            "-p",
            "no:cacheprovider",
            "/checks",
        ]
        started = time.monotonic()
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=task.constraints.timeout_seconds,
                check=False,
            )
        except FileNotFoundError as error:
            raise RunnerUnavailableError("Docker is not installed") from error
        except subprocess.TimeoutExpired as error:
            return CommandResult(
                returncode=124,
                stdout=error.stdout or "",
                stderr=error.stderr or "execution timed out",
                duration_seconds=time.monotonic() - started,
            )

        daemon_errors = (
            "Cannot connect to the Docker daemon",
            "failed to connect to the docker API",
            "Is the docker daemon running",
        )
        if result.returncode != 0 and any(message in result.stderr for message in daemon_errors):
            raise RunnerUnavailableError("Docker daemon is not running")

        return CommandResult(
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            duration_seconds=time.monotonic() - started,
        )

    def _ensure_image(self, task: Task) -> None:
        if task.image in self._prepared_images:
            return
        if task.dockerfile is None:
            self._prepared_images.add(task.image)
            return

        result = self._run_docker(
            [
                "docker",
                "build",
                "--tag",
                task.image,
                "--file",
                str(task.dockerfile.resolve()),
                str(task.root.resolve()),
            ],
            timeout=task.constraints.timeout_seconds,
        )
        if result.returncode != 0:
            raise RunnerUnavailableError(result.stderr.strip() or result.stdout.strip() or "Docker image build failed")
        self._prepared_images.add(task.image)

    def _run_docker(self, command: list[str], timeout: int) -> subprocess.CompletedProcess[str]:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except FileNotFoundError as error:
            raise RunnerUnavailableError("Docker is not installed") from error
        except subprocess.TimeoutExpired as error:
            raise RunnerUnavailableError(error.stderr or "Docker command timed out") from error

        daemon_errors = (
            "Cannot connect to the Docker daemon",
            "failed to connect to the docker API",
            "Is the docker daemon running",
        )
        if result.returncode != 0 and any(message in result.stderr for message in daemon_errors):
            raise RunnerUnavailableError("Docker daemon is not running")
        return result
