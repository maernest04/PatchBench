from pathlib import Path

import pytest

from patchbench.evaluator import evaluate, passed_command
from patchbench.models import CandidateKind, ReviewClassification, ReviewResult, ReviewScore
from patchbench.replay import replay
from patchbench.storage import FilesystemReviewStore, FilesystemRunStore, ReviewStoreError
from patchbench.task_loader import load_task


class PassingRunner:
    def run_check(self, task, workspace, check):
        return passed_command()

    def run_differential(self, task, baseline, workspace, check):
        return passed_command()


def test_saves_task_patch_and_check_artifacts(tmp_path):
    fixture = Path("fixtures/cache-invalidation")
    result = evaluate(
        load_task(fixture),
        fixture / "candidates" / "correct.patch",
        runner=PassingRunner(),
    )
    run_store = FilesystemRunStore(tmp_path / "runs")

    stored_result = run_store.save(result)
    stored_run = run_store.load(stored_result.run_id)

    assert stored_run.payload["run_id"] == stored_result.run_id
    assert (stored_run.run_directory / "candidate.patch").is_file()
    assert (stored_run.task_directory / "task.yaml").is_file()
    assert (stored_run.run_directory / "checks" / "00-public-visible-cache-behavior.stdout").is_file()


def test_replay_creates_a_linked_run(tmp_path):
    fixture = Path("fixtures/cache-invalidation")
    result = evaluate(
        load_task(fixture),
        fixture / "candidates" / "correct.patch",
        runner=PassingRunner(),
    )
    run_store = FilesystemRunStore(tmp_path / "runs")
    initial = run_store.save(result)

    replayed = replay(run_store, initial.run_id, runner=PassingRunner())
    replayed_record = run_store.load(replayed.run_id)

    assert replayed.run_id != initial.run_id
    assert replayed.replay_of == initial.run_id
    assert replayed_record.payload["replay_of"] == initial.run_id


def test_lists_saved_runs(tmp_path):
    fixture = Path("fixtures/cache-invalidation")
    run_store = FilesystemRunStore(tmp_path / "runs")
    first = run_store.save(evaluate(load_task(fixture), fixture / "candidates" / "correct.patch", runner=PassingRunner()))
    second = run_store.save(evaluate(load_task(fixture), fixture / "candidates" / "stale-cache.patch", runner=PassingRunner()))

    runs = run_store.list_runs()

    assert {run.run_id for run in runs} == {first.run_id, second.run_id}


def test_rejects_duplicate_experiment_review_attempt(tmp_path):
    fixture = Path("fixtures/cache-invalidation")
    result = ReviewResult(
        task=load_task(fixture),
        patch=fixture / "candidates" / "correct.patch",
        score=ReviewScore(ReviewClassification.CORRECT_REJECTION, "no finding"),
        finding=None,
        duration_seconds=1.0,
        candidate_kind=CandidateKind.CONTROL,
        experiment_id="experiment",
        attempt_number=1,
    )
    store = FilesystemReviewStore(tmp_path / "reviews")

    store.save(result)

    with pytest.raises(ReviewStoreError, match="review attempt already exists"):
        store.save(result)
