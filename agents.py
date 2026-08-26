import os
import shlex
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from patchbench.models import AgentMetadata, Task


class AgentConfigurationError(ValueError):
    pass


class AgentExecutionError(RuntimeError):
    pass


@dataclass(frozen=True)
class AgentBudget:
    timeout_seconds: int
    max_attempts: int
    max_tool_calls: int
    max_tokens: int
    max_cost_usd: float


@dataclass(frozen=True)
class AgentAttempt:
    patch: Path
    metadata: AgentMetadata


class AgentAdapter(Protocol):
    def generate(self, task: Task, output_directory: Path, budget: AgentBudget) -> AgentAttempt: ...


class CommandAgentAdapter:
    def __init__(self, command: tuple[str, ...]):
        self.command = command

    @classmethod
    def from_environment(cls) -> "CommandAgentAdapter":
        raw_command = os.environ.get("PATCHBENCH_AGENT_COMMAND")
        if not raw_command:
            raise AgentConfigurationError("PATCHBENCH_AGENT_COMMAND is required")
        return cls(tuple(shlex.split(raw_command)))

    def generate(self, task: Task, output_directory: Path, budget: AgentBudget) -> AgentAttempt:
        output_directory.mkdir(parents=True, exist_ok=True)
        patch = output_directory / "candidate.patch"
        started = time.monotonic()
        with tempfile.TemporaryDirectory(prefix="patchbench-agent-") as temporary_directory:
            agent_root = Path(temporary_directory)
            repository = agent_root / "repository"
            shutil.copytree(task.repository, repository)
            public_directory = task.root / "public"
            if public_directory.is_dir():
                shutil.copytree(public_directory, agent_root / "public")
            environment = os.environ | {
                "PATCHBENCH_AGENT_REPOSITORY": str(repository),
                "PATCHBENCH_AGENT_PUBLIC_DIR": str(agent_root / "public"),
                "PATCHBENCH_AGENT_OUTPUT_PATCH": str(patch),
                "PATCHBENCH_AGENT_MAX_ATTEMPTS": str(budget.max_attempts),
                "PATCHBENCH_AGENT_MAX_TOOL_CALLS": str(budget.max_tool_calls),
                "PATCHBENCH_AGENT_MAX_TOKENS": str(budget.max_tokens),
                "PATCHBENCH_AGENT_MAX_COST_USD": str(budget.max_cost_usd),
            }
            try:
                subprocess.run(
                    self.command,
                    cwd=repository,
                    env=environment,
                    capture_output=True,
                    text=True,
                    timeout=budget.timeout_seconds,
                    check=False,
                )
            except FileNotFoundError as error:
                raise AgentExecutionError("agent command is not installed") from error
            except subprocess.TimeoutExpired as error:
                raise AgentExecutionError("agent attempt timed out") from error
        duration_seconds = time.monotonic() - started
        if not patch.is_file():
            raise AgentExecutionError("agent did not produce a candidate patch")
        return AgentAttempt(
            patch=patch,
            metadata=AgentMetadata(
                adapter="command",
                duration_seconds=duration_seconds,
                attempts=1,
                max_attempts=budget.max_attempts,
                max_tool_calls=budget.max_tool_calls,
                max_tokens=budget.max_tokens,
                max_cost_usd=budget.max_cost_usd,
            ),
        )
