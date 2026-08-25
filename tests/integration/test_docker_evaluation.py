import subprocess
from pathlib import Path

import pytest

from patchbench.evaluator import evaluate
from patchbench.models import Classification
from patchbench.runner import DockerRunner
from patchbench.task_loader import load_task


@pytest.fixture(scope="module")
def docker_runner():
    available = subprocess.run(["docker", "info"], capture_output=True, text=True, check=False)
    if available.returncode != 0:
        pytest.skip("Docker daemon is unavailable")
    return DockerRunner()


@pytest.mark.parametrize(
    ("patch_name", "classification"),
    [("correct.patch", Classification.PASS), ("stale-cache.patch", Classification.FAIL)],
)
def test_docker_evaluation_classifies_fixture_candidates(docker_runner, patch_name, classification):
    fixture = Path("fixtures/cache-invalidation")

    result = evaluate(load_task(fixture), fixture / "candidates" / patch_name, runner=docker_runner)

    assert result.classification is classification
