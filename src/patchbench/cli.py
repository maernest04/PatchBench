import argparse
import json
import tempfile
from dataclasses import replace
from pathlib import Path

from patchbench.agents import AgentBudget, AgentConfigurationError, AgentExecutionError, CommandAgentAdapter
from patchbench.models import AgentMetadata, Classification, EvaluationResult
from patchbench.evaluator import evaluate
from patchbench.replay import replay
from patchbench.reporter import render_json, render_stored_text, render_text
from patchbench.storage import FilesystemRunStore, RunNotFoundError
from patchbench.task_loader import TaskValidationError, load_task


def main() -> int:
    parser = argparse.ArgumentParser(prog="patchbench")
    subcommands = parser.add_subparsers(dest="command", required=True)
    evaluate_parser = subcommands.add_parser("evaluate")
    evaluate_parser.add_argument("--task", required=True, type=Path)
    evaluate_parser.add_argument("--patch", required=True, type=Path)
    evaluate_parser.add_argument("--format", choices=("text", "json"), default="text")
    evaluate_parser.add_argument("--artifacts-dir", type=Path, default=Path("artifacts/runs"))
    agent_parser = subcommands.add_parser("agent-evaluate")
    agent_parser.add_argument("--task", required=True, type=Path)
    agent_parser.add_argument("--format", choices=("text", "json"), default="text")
    agent_parser.add_argument("--artifacts-dir", type=Path, default=Path("artifacts/runs"))
    agent_parser.add_argument("--timeout-seconds", type=int, default=600)
    agent_parser.add_argument("--max-attempts", type=int, default=1)
    agent_parser.add_argument("--max-tool-calls", type=int, default=50)
    agent_parser.add_argument("--max-tokens", type=int, default=100000)
    agent_parser.add_argument("--max-cost-usd", type=float, default=10.0)
    show_parser = subcommands.add_parser("show")
    show_parser.add_argument("run_id")
    show_parser.add_argument("--format", choices=("text", "json"), default="text")
    show_parser.add_argument("--artifacts-dir", type=Path, default=Path("artifacts/runs"))
    replay_parser = subcommands.add_parser("replay")
    replay_parser.add_argument("run_id")
    replay_parser.add_argument("--format", choices=("text", "json"), default="text")
    replay_parser.add_argument("--artifacts-dir", type=Path, default=Path("artifacts/runs"))
    arguments = parser.parse_args()

    run_store = FilesystemRunStore(arguments.artifacts_dir)

    if arguments.command == "show":
        try:
            stored_run = run_store.load(arguments.run_id)
        except RunNotFoundError as error:
            parser.error(str(error))
        print(json.dumps(stored_run.payload, sort_keys=True) if arguments.format == "json" else render_stored_text(stored_run.payload))
        return _exit_code(Classification(stored_run.payload["classification"]))

    if arguments.command == "replay":
        try:
            result = replay(run_store, arguments.run_id)
        except RunNotFoundError as error:
            parser.error(str(error))
        print(render_json(result) if arguments.format == "json" else render_text(result))
        return _exit_code(result.classification)

    try:
        task = load_task(arguments.task)
    except TaskValidationError as error:
        parser.error(str(error))

    if arguments.command == "agent-evaluate":
        budget = AgentBudget(
            timeout_seconds=arguments.timeout_seconds,
            max_attempts=arguments.max_attempts,
            max_tool_calls=arguments.max_tool_calls,
            max_tokens=arguments.max_tokens,
            max_cost_usd=arguments.max_cost_usd,
        )
        try:
            adapter = CommandAgentAdapter.from_environment()
            with tempfile.TemporaryDirectory(prefix="patchbench-agent-output-") as temporary_directory:
                attempt = adapter.generate(task, Path(temporary_directory), budget)
                result = replace(evaluate(task, attempt.patch), agent=attempt.metadata)
                result = run_store.save(result)
        except (AgentConfigurationError, AgentExecutionError) as error:
            result = run_store.save(
                EvaluationResult(
                    classification=Classification.INCONCLUSIVE,
                    task=task,
                    patch=Path("agent-output.patch"),
                    checks=(),
                    reason=str(error),
                    agent=AgentMetadata(
                        adapter="command",
                        duration_seconds=None,
                        attempts=None,
                        max_attempts=budget.max_attempts,
                        max_tool_calls=budget.max_tool_calls,
                        max_tokens=budget.max_tokens,
                        max_cost_usd=budget.max_cost_usd,
                    ),
                )
            )
    else:
        result = run_store.save(evaluate(task, arguments.patch))
    print(render_json(result) if arguments.format == "json" else render_text(result))
    return _exit_code(result.classification)


def _exit_code(classification: Classification) -> int:
    if classification is Classification.PASS:
        return 0
    if classification is Classification.FAIL:
        return 1
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
