from pathlib import Path

import pytest

from patchbench.experiments import ExperimentValidationError, load_experiment


def test_loads_codex_pilot_experiment():
    experiment = load_experiment(Path("experiments/codex-pilot-v2-terra.yaml"))

    assert experiment.identifier == "codex-pilot-v2-terra"
    assert experiment.model == "gpt-5.6-terra"
    assert experiment.attempt_count == 3
    assert len(experiment.task_keys) == 6


def test_rejects_experiment_without_tasks(tmp_path):
    path = tmp_path / "experiment.yaml"
    path.write_text("id: test\nattempt_count: 1\ntasks: []\nreviewer: {}\nbudget: {}\n")

    with pytest.raises(ExperimentValidationError, match="tasks must be a non-empty list"):
        load_experiment(path)
