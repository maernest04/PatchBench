from pathlib import Path

import yaml

from patchbench.models import Check, Constraints, Task


class TaskValidationError(ValueError):
    pass


def load_task(task_directory: Path) -> Task:
    task_path = task_directory / "task.yaml"
    try:
        raw = yaml.safe_load(task_path.read_text())
    except OSError as error:
        raise TaskValidationError(f"read task contract: {error}") from error
    except yaml.YAMLError as error:
        raise TaskValidationError(f"parse task contract: {error}") from error

    if not isinstance(raw, dict):
        raise TaskValidationError("task contract must be an object")

    identifier = _require_string(raw, "id")
    version = raw.get("version")
    if not isinstance(version, int) or version < 1:
        raise TaskValidationError("version must be a positive integer")

    repository = task_directory / _require_string(raw, "repository")
    if not repository.is_dir():
        raise TaskValidationError(f"repository does not exist: {repository}")

    runtime = _require_object(raw, "runtime")
    image = _require_string(runtime, "image")

    constraint_values = _require_object(raw, "constraints")
    timeout_seconds = _require_positive_int(constraint_values, "timeout_seconds")
    memory_megabytes = _require_positive_int(constraint_values, "memory_megabytes")

    raw_checks = raw.get("checks")
    if not isinstance(raw_checks, list) or not raw_checks:
        raise TaskValidationError("checks must be a non-empty list")

    checks = tuple(_load_check(task_directory, value, index) for index, value in enumerate(raw_checks))
    if {check.visibility for check in checks} != {"public", "hidden"}:
        raise TaskValidationError("checks must include public and hidden visibility")

    return Task(
        identifier=identifier,
        version=version,
        root=task_directory,
        repository=repository,
        image=image,
        constraints=Constraints(timeout_seconds=timeout_seconds, memory_megabytes=memory_megabytes),
        checks=checks,
    )


def _load_check(task_directory: Path, raw: object, index: int) -> Check:
    if not isinstance(raw, dict):
        raise TaskValidationError(f"checks[{index}] must be an object")
    name = _require_string(raw, "name")
    kind = _require_string(raw, "type")
    visibility = _require_string(raw, "visibility")
    if kind != "pytest":
        raise TaskValidationError(f"checks[{index}] has unsupported type: {kind}")
    if visibility not in {"public", "hidden"}:
        raise TaskValidationError(f"checks[{index}] has invalid visibility: {visibility}")
    path = task_directory / _require_string(raw, "path")
    if not path.is_dir():
        raise TaskValidationError(f"checks[{index}] path does not exist: {path}")
    return Check(name=name, kind=kind, visibility=visibility, path=path)


def _require_object(value: dict, field: str) -> dict:
    result = value.get(field)
    if not isinstance(result, dict):
        raise TaskValidationError(f"{field} must be an object")
    return result


def _require_string(value: dict, field: str) -> str:
    result = value.get(field)
    if not isinstance(result, str) or not result.strip():
        raise TaskValidationError(f"{field} must be a non-empty string")
    return result


def _require_positive_int(value: dict, field: str) -> int:
    result = value.get(field)
    if not isinstance(result, int) or result < 1:
        raise TaskValidationError(f"{field} must be a positive integer")
    return result
