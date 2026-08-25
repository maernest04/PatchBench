import json
from pathlib import Path

from patchbench.models import Check, CheckResult, Classification, CommandResult, Constraints, EvaluationResult, Task
from patchbench.reporter import render_text


def test_renders_differential_outputs_for_a_failed_check():
    task = Task(
        identifier="task",
        version=1,
        root=Path("."),
        repository=Path("."),
        image="python:3.13-slim",
        dockerfile=None,
        constraints=Constraints(timeout_seconds=1, memory_megabytes=64, cpu_cores=1),
        checks=(),
    )
    evidence = {
        "baseline": {"normalized_stdout": '[{"result":null}]'},
        "candidate": {"normalized_stdout": '[{"result":{"id":42}}]'},
    }
    result = EvaluationResult(
        classification=Classification.FAIL,
        task=task,
        patch=Path("candidate.patch"),
        checks=(
            CheckResult(
                check=Check("preserves behavior", "differential", "hidden", Path("scenario.py")),
                command=CommandResult(1, json.dumps(evidence), "behavior differs", 0.1),
            ),
        ),
        reason="hidden check failed: preserves behavior",
    )

    output = render_text(result)

    assert 'Baseline output: [{"result":null}]' in output
    assert 'Candidate output: [{"result":{"id":42}}]' in output
