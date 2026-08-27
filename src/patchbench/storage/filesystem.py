import hashlib
import json
import platform
import shutil
import sys
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from patchbench.models import EvaluationResult, ReviewResult
from patchbench.reporter import result_payload


class RunNotFoundError(ValueError):
    pass


@dataclass(frozen=True)
class StoredRun:
    run_id: str
    run_directory: Path
    payload: dict
    task_directory: Path
    patch: Path | None


class FilesystemRunStore:
    def __init__(self, root: Path):
        self.root = root

    def save(self, result: EvaluationResult, replay_of: str | None = None) -> EvaluationResult:
        run_id = f"run-{uuid4().hex[:12]}"
        stored_result = replace(result, run_id=run_id, replay_of=replay_of)
        run_directory = self.root / run_id
        checks_directory = run_directory / "checks"
        task_directory = run_directory / "task"
        run_directory.mkdir(parents=True)
        checks_directory.mkdir()
        shutil.copytree(stored_result.task.root, task_directory)

        patch_artifact = None
        if stored_result.patch.is_file():
            patch_artifact = run_directory / "candidate.patch"
            shutil.copy2(stored_result.patch, patch_artifact)

        payload = result_payload(stored_result)
        payload["created_at"] = datetime.now(UTC).isoformat()
        payload["environment"] = {
            "python": sys.version,
            "platform": platform.platform(),
            "image": stored_result.task.image,
        }
        payload["patch_sha256"] = _sha256(stored_result.patch) if stored_result.patch.is_file() else None
        payload["task_snapshot"] = "task"
        payload["patch_snapshot"] = "candidate.patch" if patch_artifact else None

        for index, check_result in enumerate(stored_result.checks):
            stem = f"{index:02d}-{check_result.check.visibility}-{check_result.check.name}"
            stdout_path = checks_directory / f"{stem}.stdout"
            stderr_path = checks_directory / f"{stem}.stderr"
            stdout_path.write_text(check_result.command.stdout)
            stderr_path.write_text(check_result.command.stderr)
            payload["checks"][index]["stdout"] = str(stdout_path.relative_to(run_directory))
            payload["checks"][index]["stderr"] = str(stderr_path.relative_to(run_directory))

        (run_directory / "result.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        return stored_result

    def load(self, run_id: str) -> StoredRun:
        run_directory = self.root / run_id
        result_path = run_directory / "result.json"
        if not result_path.is_file():
            raise RunNotFoundError(f"run does not exist: {run_id}")
        try:
            payload = json.loads(result_path.read_text())
        except json.JSONDecodeError as error:
            raise RunNotFoundError(f"run record is invalid: {run_id}") from error
        task_directory = run_directory / payload.get("task_snapshot", "task")
        patch_snapshot = payload.get("patch_snapshot")
        patch = run_directory / patch_snapshot if isinstance(patch_snapshot, str) else None
        return StoredRun(
            run_id=run_id,
            run_directory=run_directory,
            payload=payload,
            task_directory=task_directory,
            patch=patch,
        )

    def list_runs(self) -> tuple[StoredRun, ...]:
        if not self.root.is_dir():
            return ()
        return tuple(
            self.load(path.name)
            for path in sorted(self.root.iterdir())
            if path.is_dir() and path.name.startswith("run-") and (path / "result.json").is_file()
        )


class FilesystemReviewStore:
    def __init__(self, root: Path):
        self.root = root

    def save(self, result: ReviewResult) -> ReviewResult:
        review_id = f"review-{uuid4().hex[:12]}"
        stored_result = replace(result, review_id=review_id)
        review_directory = self.root / review_id
        review_directory.mkdir(parents=True)
        if stored_result.patch.is_file():
            shutil.copy2(stored_result.patch, review_directory / "candidate.patch")
        payload = {
            "review_id": review_id,
            "task": {"id": stored_result.task.identifier, "version": stored_result.task.version},
            "patch_sha256": _sha256(stored_result.patch) if stored_result.patch.is_file() else None,
            "score": stored_result.score.classification,
            "reason": stored_result.score.reason,
            "finding": _finding_payload(stored_result),
            "duration_seconds": stored_result.duration_seconds,
            "created_at": datetime.now(UTC).isoformat(),
        }
        (review_directory / "result.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        return stored_result


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _finding_payload(result: ReviewResult) -> dict | None:
    if result.finding is None:
        return None
    return {
        "category": result.finding.category,
        "affected_paths": result.finding.affected_paths,
        "affected_symbols": result.finding.affected_symbols,
        "rationale": result.finding.rationale,
    }
