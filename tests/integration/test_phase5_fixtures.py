from pathlib import Path

import pytest

from patchbench.evaluator import evaluate
from patchbench.models import Classification
from patchbench.task_loader import load_task


@pytest.mark.parametrize(
    ("fixture_name", "patch_name", "classification"),
    [
        ("api-user-directory", "correct.patch", Classification.PASS),
        ("api-user-directory", "incompatible.patch", Classification.FAIL),
        ("refactor-pricing", "correct.patch", Classification.PASS),
        ("refactor-pricing", "breaking-refactor.patch", Classification.FAIL),
        ("redacted-audit-log", "correct.patch", Classification.PASS),
        ("redacted-audit-log", "leaks-secret.patch", Classification.FAIL),
        ("retry-delivery", "correct.patch", Classification.PASS),
        ("retry-delivery", "retry-duplicates.patch", Classification.FAIL),
    ],
)
def test_phase5_fixtures_classify_candidates(docker_runner, fixture_name, patch_name, classification):
    fixture = Path("fixtures") / fixture_name

    result = evaluate(load_task(fixture), fixture / "candidates" / patch_name, runner=docker_runner)

    assert result.classification is classification
