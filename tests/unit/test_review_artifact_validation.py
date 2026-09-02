from pathlib import Path

from patchbench.models import CandidateKind, CommandResult, ReviewClassification, ReviewerFinding
from patchbench.review_artifact_validation import validate_artifact
from patchbench.review_scoring import score_finding
from patchbench.task_loader import load_task


class ArtifactRunner:
    def __init__(self):
        self.returncodes = iter((1, 0))

    def run_command(self, task, workspace, command):
        return CommandResult(next(self.returncodes), "", "", 0.1)


def test_validates_artifact_and_scores_executable_detection():
    task = load_task(Path("fixtures/cache-invalidation"))
    validation = validate_artifact(task, ("python", "-c", "raise SystemExit(1)"), runner=ArtifactRunner())
    finding = ReviewerFinding(
        category="preservation",
        affected_paths=("user_store.py",),
        affected_symbols=(),
        rationale="Deletion leaves a cached user readable.",
        verification_command=("python", "-c", "raise SystemExit(1)"),
    )

    score = score_finding(task, finding, CandidateKind.KNOWN_REGRESSION, validation)

    assert validation.passed
    assert score.classification is ReviewClassification.EXECUTABLE_DETECTED
