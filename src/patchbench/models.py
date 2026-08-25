from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class Classification(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass(frozen=True)
class Constraints:
    timeout_seconds: int
    memory_megabytes: int
    cpu_cores: float


@dataclass(frozen=True)
class Check:
    name: str
    kind: str
    visibility: str
    path: Path | None = None
    command: tuple[str, ...] = ()
    expected_exit_code: int = 0
    expected_stdout: str = ""
    expected_files: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class Task:
    identifier: str
    version: int
    root: Path
    repository: Path
    image: str
    dockerfile: Path | None
    constraints: Constraints
    checks: tuple[Check, ...]


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str
    duration_seconds: float


@dataclass(frozen=True)
class CheckResult:
    check: Check
    command: CommandResult


@dataclass(frozen=True)
class EvaluationResult:
    classification: Classification
    task: Task
    patch: Path
    checks: tuple[CheckResult, ...]
    reason: str | None = None
    run_id: str | None = None
    replay_of: str | None = None
