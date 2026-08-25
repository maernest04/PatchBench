from pathlib import Path

import pytest

from patchbench.evaluator import evaluate
from patchbench.models import Classification
from patchbench.runner import DockerRunner
from patchbench.task_loader import load_task


@pytest.mark.parametrize(
    ("patch_name", "classification"),
    [("correct.patch", Classification.PASS), ("superficial.patch", Classification.FAIL)],
)
def test_cli_contract_separates_fixture_candidates(docker_runner, patch_name, classification):
    fixture = Path("fixtures/cli-report-generation")

    result = evaluate(load_task(fixture), fixture / "candidates" / patch_name, runner=docker_runner)

    assert result.classification is classification
