from patchbench.evaluator import evaluate
from patchbench.runner import DockerRunner
from patchbench.storage import FilesystemRunStore, RunNotFoundError
from patchbench.task_loader import TaskValidationError, load_task


def replay(run_store: FilesystemRunStore, run_id: str, runner: DockerRunner | None = None):
    stored_run = run_store.load(run_id)
    if stored_run.patch is None or not stored_run.patch.is_file():
        raise RunNotFoundError(f"run has no replayable patch: {run_id}")
    try:
        task = load_task(stored_run.task_directory)
    except TaskValidationError as error:
        raise RunNotFoundError(f"run task snapshot is invalid: {run_id}: {error}") from error
    result = evaluate(task, stored_run.patch, runner=runner)
    return run_store.save(result, replay_of=run_id)
