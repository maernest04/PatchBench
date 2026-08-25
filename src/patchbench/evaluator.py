from pathlib import Path

from patchbench.models import CheckResult, Classification, CommandResult, EvaluationResult, Task
from patchbench.runner import DockerRunner, RunnerUnavailableError
from patchbench.workspace import PatchApplicationError, PatchValidationError, create_candidate_workspace, create_workspace


def evaluate(task: Task, patch: Path, runner: DockerRunner | None = None) -> EvaluationResult:
    active_runner = runner or DockerRunner()
    try:
        temporary_directory = create_candidate_workspace(task.repository, patch)
    except (PatchValidationError, PatchApplicationError) as error:
        return EvaluationResult(
            classification=Classification.INCONCLUSIVE,
            task=task,
            patch=patch,
            checks=(),
            reason=str(error),
        )

    baseline_directory = create_workspace(task.repository)
    with temporary_directory, baseline_directory:
        workspace = Path(temporary_directory.name) / "repository"
        baseline = Path(baseline_directory.name) / "repository"
        check_results: list[CheckResult] = []
        failure_reason = None
        try:
            for check in task.checks:
                if check.kind == "differential":
                    command = active_runner.run_differential(task, baseline, workspace, check)
                else:
                    command = active_runner.run_check(task, workspace, check)
                result = CheckResult(check=check, command=command)
                check_results.append(result)
                if command.returncode != 0 and failure_reason is None:
                    failure_reason = f"{check.visibility} check failed: {check.name}"
        except RunnerUnavailableError as error:
            return EvaluationResult(
                classification=Classification.INCONCLUSIVE,
                task=task,
                patch=patch,
                checks=tuple(check_results),
                reason=str(error),
            )

    if failure_reason:
        return EvaluationResult(
            classification=Classification.FAIL,
            task=task,
            patch=patch,
            checks=tuple(check_results),
            reason=failure_reason,
        )

    return EvaluationResult(
        classification=Classification.PASS,
        task=task,
        patch=patch,
        checks=tuple(check_results),
    )


def passed_command() -> CommandResult:
    return CommandResult(returncode=0, stdout="", stderr="", duration_seconds=0.0)
