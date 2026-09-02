from pathlib import Path

from patchbench.models import ArtifactValidation, CandidateKind, Task
from patchbench.runner import DockerRunner, RunnerUnavailableError
from patchbench.workspace import PatchApplicationError, PatchValidationError, create_candidate_workspace


class ArtifactValidationError(RuntimeError):
    pass


def validate_artifact(task: Task, command: tuple[str, ...], runner: DockerRunner | None = None) -> ArtifactValidation:
    control = next((candidate for candidate in task.candidates if candidate.kind is CandidateKind.CONTROL), None)
    regression = next((candidate for candidate in task.candidates if candidate.kind is CandidateKind.KNOWN_REGRESSION), None)
    if control is None or regression is None:
        raise ArtifactValidationError(f"task does not have registered candidates: {task.identifier}")
    active_runner = runner or DockerRunner()
    try:
        with create_candidate_workspace(task.repository, regression.patch) as regression_workspace, create_candidate_workspace(
            task.repository, control.patch
        ) as control_workspace:
            candidate_result = active_runner.run_command(task, Path(regression_workspace) / "repository", command)
            control_result = active_runner.run_command(task, Path(control_workspace) / "repository", command)
    except (PatchValidationError, PatchApplicationError, RunnerUnavailableError) as error:
        raise ArtifactValidationError(str(error)) from error
    passed = candidate_result.returncode != 0 and control_result.returncode == 0
    return ArtifactValidation(
        passed,
        "artifact fails on the known regression and passes on the control"
        if passed
        else "artifact does not distinguish the known regression from the control",
        candidate_result,
        control_result,
    )
