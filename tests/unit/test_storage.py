from pathlib import Path

from patchbench.evaluator import evaluate, passed_command
from patchbench.replay import replay
from patchbench.storage import FilesystemRunStore
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
