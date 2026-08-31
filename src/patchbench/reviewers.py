import json
import os
import shlex
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from patchbench.models import ReviewerFinding, Task
from patchbench.workspace import PatchApplicationError, PatchValidationError, create_candidate_workspace


class ReviewerConfigurationError(ValueError):
    pass


class ReviewerExecutionError(RuntimeError):
    pass


@dataclass(frozen=True)
class ReviewerBudget:
    timeout_seconds: int
    max_tool_calls: int
    max_tokens: int
    max_cost_usd: float


@dataclass(frozen=True)
class ReviewerAttempt:
    finding: ReviewerFinding | None
    duration_seconds: float


class ReviewerAdapter(Protocol):
    def review(self, task: Task, patch: Path, output_directory: Path, budget: ReviewerBudget) -> ReviewerAttempt: ...


class CommandReviewerAdapter:
    def __init__(self, command: tuple[str, ...], environment: dict[str, str] | None = None):
        self.command = command
        self.environment = environment or {}

    @classmethod
    def from_environment(cls) -> "CommandReviewerAdapter":
        raw_command = os.environ.get("PATCHBENCH_REVIEWER_COMMAND")
        if not raw_command:
            raise ReviewerConfigurationError("PATCHBENCH_REVIEWER_COMMAND is required")
        return cls(tuple(shlex.split(raw_command)))

    def review(self, task: Task, patch: Path, output_directory: Path, budget: ReviewerBudget) -> ReviewerAttempt:
        output_directory.mkdir(parents=True, exist_ok=True)
        output_path = output_directory / "review.json"
        started = time.monotonic()
        try:
            with create_candidate_workspace(task.repository, patch) as candidate_directory:
                with tempfile.TemporaryDirectory(prefix="patchbench-reviewer-") as temporary_directory:
                    reviewer_root = Path(temporary_directory)
                    repository = reviewer_root / "repository"
                    shutil.copytree(Path(candidate_directory) / "repository", repository)
                    public_directory = task.root / "public"
                    if public_directory.is_dir():
                        shutil.copytree(public_directory, reviewer_root / "public")
                    candidate_patch = reviewer_root / "candidate.patch"
                    shutil.copy2(patch, candidate_patch)
                    environment = os.environ | self.environment | {
                        "PATCHBENCH_REVIEWER_REPOSITORY": str(repository),
                        "PATCHBENCH_REVIEWER_PUBLIC_DIR": str(reviewer_root / "public"),
                        "PATCHBENCH_REVIEWER_PATCH": str(candidate_patch),
                        "PATCHBENCH_REVIEWER_OUTPUT": str(output_path),
                        "PATCHBENCH_REVIEWER_MAX_TOOL_CALLS": str(budget.max_tool_calls),
                        "PATCHBENCH_REVIEWER_MAX_TOKENS": str(budget.max_tokens),
                        "PATCHBENCH_REVIEWER_MAX_COST_USD": str(budget.max_cost_usd),
                    }
                    try:
                        result = subprocess.run(
                            self.command,
                            cwd=repository,
                            env=environment,
                            capture_output=True,
                            text=True,
                            timeout=budget.timeout_seconds,
                            check=False,
                        )
                    except FileNotFoundError as error:
                        raise ReviewerExecutionError("reviewer command is not installed") from error
                    except subprocess.TimeoutExpired as error:
                        raise ReviewerExecutionError("reviewer attempt timed out") from error
                    if result.returncode != 0:
                        raise ReviewerExecutionError("reviewer command failed")
        except (PatchValidationError, PatchApplicationError) as error:
            raise ReviewerExecutionError(str(error)) from error
        if not output_path.is_file():
            raise ReviewerExecutionError("reviewer did not produce a finding")
        return ReviewerAttempt(finding=_load_finding(output_path), duration_seconds=time.monotonic() - started)


def _load_finding(path: Path) -> ReviewerFinding | None:
    try:
        raw = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ReviewerExecutionError("reviewer output is not valid JSON") from error
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise ReviewerExecutionError("reviewer output must be an object or null")
    category = raw.get("category")
    rationale = raw.get("rationale")
    affected_paths = _load_strings(raw, "affected_paths")
    affected_symbols = _load_strings(raw, "affected_symbols")
    if category not in {"correctness", "preservation", "safety", "reliability", "efficiency"}:
        raise ReviewerExecutionError("reviewer output has an invalid category")
    if not isinstance(rationale, str) or not rationale.strip():
        raise ReviewerExecutionError("reviewer output rationale must be a non-empty string")
    return ReviewerFinding(category, affected_paths, affected_symbols, rationale)


def _load_strings(raw: dict, field: str) -> tuple[str, ...]:
    values = raw.get(field)
    if not isinstance(values, list) or any(not isinstance(value, str) or not value.strip() for value in values):
        raise ReviewerExecutionError(f"reviewer output {field} must be a list of strings")
    return tuple(values)
