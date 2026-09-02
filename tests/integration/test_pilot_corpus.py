from pathlib import Path

import pytest

from patchbench.evaluator import evaluate
from patchbench.models import CandidateKind, Classification
from patchbench.replay import replay
from patchbench.storage import FilesystemRunStore
from patchbench.task_loader import load_task


@pytest.mark.parametrize(
    "fixture_name",
    (
        "api-user-directory",
        "atomic-export",
        "callback-ordering",
        "cache-invalidation",
        "cli-report-generation",
        "collection-reset",
        "input-encoding",
        "optional-field-compatibility",
        "pagination-compatibility",
        "parameter-alias",
        "redacted-audit-log",
        "refactor-pricing",
        "retry-delivery",
        "retry-backoff",
        "session-expiry",
        "timeout-cleanup",
        "token-log-redaction",
        "workspace-path-authorization",
    ),
)
def test_pilot_candidates_pass_public_checks_fail_hidden_regressions_and_replay(docker_runner, fixture_name, tmp_path):
    task = load_task(Path("fixtures") / fixture_name)
    candidates = {candidate.kind: candidate for candidate in task.candidates}
    control = evaluate(task, candidates[CandidateKind.CONTROL].patch, runner=docker_runner)
    regression = evaluate(task, candidates[CandidateKind.KNOWN_REGRESSION].patch, runner=docker_runner)

    assert control.classification is Classification.PASS
    assert regression.classification is Classification.FAIL
    assert all(check.command.returncode == 0 for check in regression.checks if check.check.visibility == "public")
    assert any(check.command.returncode != 0 for check in regression.checks if check.check.visibility == "hidden")

    store = FilesystemRunStore(tmp_path / fixture_name)
    stored = store.save(regression)
    replayed = replay(store, stored.run_id, runner=docker_runner)

    assert replayed.classification is Classification.FAIL
