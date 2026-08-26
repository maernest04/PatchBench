import json
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
        command = self._container_command(task, workspace)
        command.extend(
            [
                "--mount",
                f"type=bind,source={check.path.resolve()},target=/checks,readonly",
                task.image,
                "python",
                "-m",
                "pytest",
                "-p",
                "no:cacheprovider",
                "/checks",
            ]
        )
        return self._run_check_command(command, task.constraints.timeout_seconds)

    def run_differential(self, task: Task, baseline: Path, candidate: Path, check: Check) -> CommandResult:
        self._ensure_image(task)
        baseline_result = self._run_scenario(task, baseline, check.path)
        candidate_result = self._run_scenario(task, candidate, check.path)
        payload = {
            "baseline": _command_payload(baseline_result),
            "candidate": _command_payload(candidate_result),
        }
        if baseline_result.returncode != 0 or candidate_result.returncode != 0:
            return CommandResult(
                returncode=1,
                stdout=json.dumps(payload, sort_keys=True),
                stderr="differential scenario execution failed",
                duration_seconds=baseline_result.duration_seconds + candidate_result.duration_seconds,
            )

        baseline_output = _normalize_output(baseline_result.stdout)
        candidate_output = _normalize_output(candidate_result.stdout)
        payload["baseline"]["normalized_stdout"] = baseline_output
        payload["candidate"]["normalized_stdout"] = candidate_output
        return CommandResult(
            returncode=0 if baseline_output == candidate_output else 1,
            stdout=json.dumps(payload, sort_keys=True),
            stderr="" if baseline_output == candidate_output else "baseline and candidate behavior differ",
            duration_seconds=baseline_result.duration_seconds + candidate_result.duration_seconds,
        )

    def run_cli(self, task: Task, workspace: Path, check: Check) -> CommandResult:
        self._ensure_image(task)
        command = self._container_command(task, workspace)
        expectation = {
            "command": check.command,
            "exit_code": check.expected_exit_code,
            "stdout": check.expected_stdout,
            "files": dict(check.expected_files),
        }
        command.extend(
            [
                "--mount",
                f"type=bind,source={Path(__file__).with_name('cli_check.py').resolve()},target=/cli_check.py,readonly",
                task.image,
                "python",
                "/cli_check.py",
                json.dumps(expectation, sort_keys=True),
            ]
        )
        return self._run_check_command(command, task.constraints.timeout_seconds)

    def run_api(self, task: Task, workspace: Path, check: Check) -> CommandResult:
        assert check.path is not None
        result = self._run_scenario(task, workspace, check.path)
        if result.returncode != 0:
            return result
        observed = _normalize_output(result.stdout)
        expected = _normalize_output(check.expected_stdout)
        payload = {"expected": expected, "observed": observed}
        return CommandResult(
            returncode=0 if observed == expected else 1,
            stdout=json.dumps(payload, sort_keys=True),
            stderr="" if observed == expected else "API behavior does not match the contract",
            duration_seconds=result.duration_seconds,
        )

    def _run_scenario(self, task: Task, workspace: Path, scenario: Path) -> CommandResult:
        command = self._container_command(task, workspace)
        command.extend(
            [
                "--mount",
                f"type=bind,source={scenario.resolve()},target=/scenario.py,readonly",
                task.image,
                "python",
                "/scenario.py",
            ]
        )
        return self._run_check_command(command, task.constraints.timeout_seconds)

    def _container_command(self, task: Task, workspace: Path) -> list[str]:
        return [
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
            "--cpus",
            str(task.constraints.cpu_cores),
            "--pids-limit",
            "256",
            "--mount",
            f"type=bind,source={workspace.resolve()},target=/workspace,readonly",
            "--workdir",
            "/workspace",
            "--env",
            "PYTHONDONTWRITEBYTECODE=1",
            "--env",
            "PYTHONPATH=/workspace",
        ]

    def _run_check_command(self, command: list[str], timeout: int) -> CommandResult:
        started = time.monotonic()
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


def _command_payload(result: CommandResult) -> dict:
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "duration_seconds": result.duration_seconds,
    }


def _normalize_output(output: str) -> str:
    try:
        return json.dumps(json.loads(output), sort_keys=True, separators=(",", ":"))
    except json.JSONDecodeError:
        return output.strip()
