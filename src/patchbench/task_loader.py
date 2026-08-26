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
    dockerfile_value = runtime.get("dockerfile")
    dockerfile = None
    if dockerfile_value is not None:
        if not isinstance(dockerfile_value, str) or not dockerfile_value.strip():
            raise TaskValidationError("runtime.dockerfile must be a non-empty string")
        dockerfile = task_directory / dockerfile_value
        if not dockerfile.is_file():
            raise TaskValidationError(f"runtime.dockerfile does not exist: {dockerfile}")

    constraint_values = _require_object(raw, "constraints")
    timeout_seconds = _require_positive_int(constraint_values, "timeout_seconds")
    memory_megabytes = _require_positive_int(constraint_values, "memory_megabytes")
    cpu_cores = _require_positive_number(constraint_values, "cpu_cores")

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
        dockerfile=dockerfile,
        constraints=Constraints(
            timeout_seconds=timeout_seconds,
            memory_megabytes=memory_megabytes,
            cpu_cores=cpu_cores,
        ),
        checks=checks,
    )


def _load_check(task_directory: Path, raw: object, index: int) -> Check:
    if not isinstance(raw, dict):
        raise TaskValidationError(f"checks[{index}] must be an object")
    name = _require_string(raw, "name")
    kind = _require_string(raw, "type")
    visibility = _require_string(raw, "visibility")
    if kind not in {"pytest", "differential", "cli", "api"}:
        raise TaskValidationError(f"checks[{index}] has unsupported type: {kind}")
    if visibility not in {"public", "hidden"}:
        raise TaskValidationError(f"checks[{index}] has invalid visibility: {visibility}")
    path = None
    if kind in {"pytest", "differential", "api"}:
        path = task_directory / _require_string(raw, "path")
        if not path.exists() or (kind == "pytest" and not path.is_dir()) or (kind in {"differential", "api"} and not path.is_file()):
            raise TaskValidationError(f"checks[{index}] path does not exist: {path}")
    if kind in {"pytest", "differential"}:
        return Check(name=name, kind=kind, visibility=visibility, path=path)
    expected = _require_object(raw, "expected")
    if kind == "api":
        expected_stdout = expected.get("stdout")
        if not isinstance(expected_stdout, str):
            raise TaskValidationError(f"checks[{index}].expected.stdout must be a string")
        return Check(name=name, kind=kind, visibility=visibility, path=path, expected_stdout=expected_stdout)
    command = _require_command(raw, index)
    expected_exit_code = expected.get("exit_code", 0)
    if not isinstance(expected_exit_code, int) or isinstance(expected_exit_code, bool):
        raise TaskValidationError(f"checks[{index}].expected.exit_code must be an integer")
    expected_stdout = expected.get("stdout", "")
    if not isinstance(expected_stdout, str):
        raise TaskValidationError(f"checks[{index}].expected.stdout must be a string")
    expected_files = _load_expected_files(expected, index)
    return Check(
        name=name,
        kind=kind,
        visibility=visibility,
        command=command,
        expected_exit_code=expected_exit_code,
        expected_stdout=expected_stdout,
        expected_files=expected_files,
    )


def _require_command(value: dict, index: int) -> tuple[str, ...]:
    command = value.get("command")
    if not isinstance(command, list) or not command or any(not isinstance(item, str) or not item for item in command):
        raise TaskValidationError(f"checks[{index}].command must be a non-empty list of strings")
    return tuple(command)


def _load_expected_files(value: dict, index: int) -> tuple[tuple[str, str], ...]:
    files = value.get("files", {})
    if not isinstance(files, dict):
        raise TaskValidationError(f"checks[{index}].expected.files must be an object")
    loaded = []
    for path, content in files.items():
        if not isinstance(path, str) or not path or Path(path).is_absolute() or ".." in Path(path).parts:
            raise TaskValidationError(f"checks[{index}].expected.files has an unsafe path")
        if not isinstance(content, str):
            raise TaskValidationError(f"checks[{index}].expected.files values must be strings")
        loaded.append((path, content))
    return tuple(loaded)


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


def _require_positive_number(value: dict, field: str) -> float:
    result = value.get(field)
    if not isinstance(result, (int, float)) or isinstance(result, bool) or result <= 0:
        raise TaskValidationError(f"{field} must be a positive number")
    return float(result)
