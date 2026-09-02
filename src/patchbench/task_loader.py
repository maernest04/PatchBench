from pathlib import Path

import yaml

from patchbench.models import REVIEW_CATEGORIES, Candidate, CandidateKind, Check, Constraints, ReviewerGroundTruth, Task


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
    candidates = _load_candidates(task_directory, raw)
    reviewer_ground_truth = _load_reviewer_ground_truth(task_directory, raw)

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
        candidates=candidates,
        reviewer_ground_truth=reviewer_ground_truth,
    )


def _load_candidates(task_directory: Path, raw: dict) -> tuple[Candidate, ...]:
    values = raw.get("candidates")
    if not isinstance(values, list) or not values:
        raise TaskValidationError("candidates must be a non-empty list")
    candidates = []
    for index, value in enumerate(values):
        if not isinstance(value, dict):
            raise TaskValidationError(f"candidates[{index}] must be an object")
        path_value = _require_string(value, "path")
        path = Path(path_value)
        if path.is_absolute() or ".." in path.parts:
            raise TaskValidationError(f"candidates[{index}].path has an unsafe path")
        patch = task_directory / path
        if not patch.is_file():
            raise TaskValidationError(f"candidates[{index}].path does not exist: {patch}")
        kind_value = _require_string(value, "kind")
        try:
            kind = CandidateKind(kind_value)
        except ValueError as error:
            raise TaskValidationError(f"candidates[{index}].kind is invalid: {kind_value}") from error
        provenance = _require_string(value, "provenance")
        if provenance not in {"human_authored", "observed_ai_style"}:
            raise TaskValidationError(f"candidates[{index}].provenance is invalid: {provenance}")
        candidates.append(Candidate(patch=patch, kind=kind, provenance=provenance))
    if {candidate.kind for candidate in candidates} != {CandidateKind.CONTROL, CandidateKind.KNOWN_REGRESSION}:
        raise TaskValidationError("candidates must include one control and one known_regression")
    if len({candidate.patch for candidate in candidates}) != len(candidates):
        raise TaskValidationError("candidates must not repeat a patch")
    return tuple(candidates)


def _load_reviewer_ground_truth(task_directory: Path, raw: dict) -> ReviewerGroundTruth | None:
    value = raw.get("reviewer_ground_truth")
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise TaskValidationError("reviewer_ground_truth must be a non-empty string")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise TaskValidationError("reviewer_ground_truth has an unsafe path")
    ground_truth_path = task_directory / path
    try:
        raw_ground_truth = yaml.safe_load(ground_truth_path.read_text())
    except OSError as error:
        raise TaskValidationError(f"read reviewer ground truth: {error}") from error
    except yaml.YAMLError as error:
        raise TaskValidationError(f"parse reviewer ground truth: {error}") from error
    if not isinstance(raw_ground_truth, dict):
        raise TaskValidationError("reviewer ground truth must be an object")
    category = _require_string(raw_ground_truth, "category")
    if category not in REVIEW_CATEGORIES:
        raise TaskValidationError(f"reviewer ground truth has invalid category: {category}")
    return ReviewerGroundTruth(
        fault_id=_require_string(raw_ground_truth, "fault_id"),
        category=category,
        affected_paths=_load_reviewer_evidence(raw_ground_truth, "affected_paths"),
        affected_symbols=_load_reviewer_evidence(raw_ground_truth, "affected_symbols"),
    )


def _load_reviewer_evidence(value: dict, field: str) -> tuple[str, ...]:
    raw_values = value.get(field)
    if not isinstance(raw_values, list) or not raw_values or any(not isinstance(item, str) or not item.strip() for item in raw_values):
        raise TaskValidationError(f"reviewer ground truth.{field} must be a non-empty list of strings")
    return tuple(raw_values)


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
    category = raw.get("category", "correctness")
    if not isinstance(category, str) or category not in REVIEW_CATEGORIES:
        raise TaskValidationError(f"checks[{index}] has invalid category: {category}")
    path = None
    if kind in {"pytest", "differential", "api"}:
        path = task_directory / _require_string(raw, "path")
        if not path.exists() or (kind == "pytest" and not path.is_dir()) or (kind in {"differential", "api"} and not path.is_file()):
            raise TaskValidationError(f"checks[{index}] path does not exist: {path}")
    if kind in {"pytest", "differential"}:
        return Check(name=name, kind=kind, visibility=visibility, path=path, category=category)
    expected = _require_object(raw, "expected")
    if kind == "api":
        expected_stdout = expected.get("stdout")
        if not isinstance(expected_stdout, str):
            raise TaskValidationError(f"checks[{index}].expected.stdout must be a string")
        return Check(name=name, kind=kind, visibility=visibility, path=path, expected_stdout=expected_stdout, category=category)
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
        category=category,
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
