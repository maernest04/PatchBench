from dataclasses import dataclass
from pathlib import Path

import yaml

from patchbench.models import ReviewWorkflow


class ExperimentValidationError(ValueError):
    pass


@dataclass(frozen=True)
class Experiment:
    identifier: str
    corpus: str
    workflow: ReviewWorkflow
    task_keys: tuple[str, ...]
    reviewer_adapter: str
    model: str
    prompt_version: str
    timeout_seconds: int
    max_tool_calls: int
    max_tokens: int
    max_cost_usd: float
    attempt_count: int


def load_experiment(path: Path) -> Experiment:
    try:
        raw = yaml.safe_load(path.read_text())
    except OSError as error:
        raise ExperimentValidationError(f"read experiment: {error}") from error
    except yaml.YAMLError as error:
        raise ExperimentValidationError(f"parse experiment: {error}") from error
    if not isinstance(raw, dict):
        raise ExperimentValidationError("experiment must be an object")
    reviewer = _require_object(raw, "reviewer")
    budget = _require_object(raw, "budget")
    tasks = raw.get("tasks")
    if not isinstance(tasks, list) or not tasks or any(not isinstance(task, str) or not task.strip() for task in tasks):
        raise ExperimentValidationError("tasks must be a non-empty list of strings")
    return Experiment(
        identifier=_require_string(raw, "id"),
        corpus=_require_string(raw, "corpus"),
        workflow=_load_workflow(raw),
        task_keys=tuple(tasks),
        reviewer_adapter=_require_string(reviewer, "adapter"),
        model=_require_string(reviewer, "model"),
        prompt_version=_require_string(reviewer, "prompt_version"),
        timeout_seconds=_require_positive_int(budget, "timeout_seconds"),
        max_tool_calls=_require_positive_int(budget, "max_tool_calls"),
        max_tokens=_require_positive_int(budget, "max_tokens"),
        max_cost_usd=_require_positive_number(budget, "max_cost_usd"),
        attempt_count=_require_positive_int(raw, "attempt_count"),
    )


def _load_workflow(raw: dict) -> ReviewWorkflow:
    try:
        return ReviewWorkflow(_require_string(raw, "workflow"))
    except ValueError as error:
        raise ExperimentValidationError("workflow is invalid") from error


def _require_object(raw: dict, field: str) -> dict:
    value = raw.get(field)
    if not isinstance(value, dict):
        raise ExperimentValidationError(f"{field} must be an object")
    return value


def _require_string(raw: dict, field: str) -> str:
    value = raw.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ExperimentValidationError(f"{field} must be a non-empty string")
    return value


def _require_positive_int(raw: dict, field: str) -> int:
    value = raw.get(field)
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ExperimentValidationError(f"{field} must be a positive integer")
    return value


def _require_positive_number(raw: dict, field: str) -> float:
    value = raw.get(field)
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
        raise ExperimentValidationError(f"{field} must be a positive number")
    return float(value)
