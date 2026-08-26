import sys
from pathlib import Path

import pytest

from patchbench.agents import AgentBudget, AgentConfigurationError, CommandAgentAdapter
from patchbench.evaluator import evaluate
from patchbench.models import CommandResult
from patchbench.task_loader import load_task


class PassingRunner:
    def run_check(self, task, workspace, check):
        return CommandResult(0, "", "", 0.0)

    def run_differential(self, task, baseline, workspace, check):
        return CommandResult(0, "", "", 0.0)


def test_command_adapter_exposes_only_public_task_material(tmp_path):
    fixture = Path("fixtures/cache-invalidation")
    patch = (fixture / "candidates" / "correct.patch").read_text()
    script = tmp_path / "agent.py"
    script.write_text(
        "\n".join(
            [
                "import os",
                "from pathlib import Path",
                "repository = Path(os.environ['PATCHBENCH_AGENT_REPOSITORY'])",
                "assert (Path(os.environ['PATCHBENCH_AGENT_PUBLIC_DIR']) / 'task.md').is_file()",
                "assert not (repository.parent / 'hidden').exists()",
                f"Path(os.environ['PATCHBENCH_AGENT_OUTPUT_PATCH']).write_text({patch!r})",
            ]
        )
    )
    adapter = CommandAgentAdapter((sys.executable, str(script)))
    budget = AgentBudget(10, 1, 5, 1000, 1.0)

    attempt = adapter.generate(load_task(fixture), tmp_path / "output", budget)
    result = evaluate(load_task(fixture), attempt.patch, runner=PassingRunner())

    assert attempt.patch.is_file()
    assert attempt.metadata.adapter == "command"
    assert attempt.metadata.max_tokens == 1000
    assert result.classification == "PASS"


def test_command_adapter_requires_environment_configuration(monkeypatch):
    monkeypatch.delenv("PATCHBENCH_AGENT_COMMAND", raising=False)

    with pytest.raises(AgentConfigurationError, match="PATCHBENCH_AGENT_COMMAND is required"):
        CommandAgentAdapter.from_environment()
