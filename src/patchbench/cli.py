import argparse
import json
import tempfile
from dataclasses import replace
from pathlib import Path

from patchbench.agents import AgentBudget, AgentConfigurationError, AgentExecutionError, CommandAgentAdapter
from patchbench.benchmark import build_report, build_review_report
from patchbench.codex import CodexRunError, run_codex
from patchbench.models import AgentMetadata, Classification, EvaluationResult, ReviewClassification, ReviewResult, ReviewScore
from patchbench.evaluator import evaluate
from patchbench.replay import replay
from patchbench.reporter import render_json, render_review_json, render_review_text, render_stored_text, render_text
from patchbench.review_scoring import score_finding
from patchbench.reviewers import CommandReviewerAdapter, ReviewerBudget, ReviewerConfigurationError, ReviewerExecutionError
from patchbench.storage import FilesystemReviewStore, FilesystemRunStore, ReviewStoreError, RunNotFoundError
from patchbench.task_loader import TaskValidationError, load_task
from patchbench.working_tree import WorkingTreeError, write_working_tree_patch


def main() -> int:
    parser = argparse.ArgumentParser(prog="patchbench")
    subcommands = parser.add_subparsers(dest="command", required=True)
    evaluate_parser = subcommands.add_parser("evaluate")
    evaluate_parser.add_argument("--task", required=True, type=Path)
    evaluate_parser.add_argument("--patch", required=True, type=Path)
    evaluate_parser.add_argument("--format", choices=("text", "json"), default="text")
    evaluate_parser.add_argument("--artifacts-dir", type=Path, default=Path("artifacts/runs"))
    working_tree_parser = subcommands.add_parser("verify-working-tree")
    working_tree_parser.add_argument("--task", required=True, type=Path)
    working_tree_parser.add_argument("--format", choices=("text", "json"), default="text")
    working_tree_parser.add_argument("--artifacts-dir", type=Path, default=Path("artifacts/runs"))
    codex_parser = subcommands.add_parser("codex-run")
    codex_parser.add_argument("--task", required=True, type=Path)
    codex_parser.add_argument("--prompt", required=True)
    codex_parser.add_argument("--format", choices=("text", "json"), default="text")
    codex_parser.add_argument("--artifacts-dir", type=Path, default=Path("artifacts/runs"))
    agent_parser = subcommands.add_parser("agent-evaluate")
    agent_parser.add_argument("--task", required=True, type=Path)
    agent_parser.add_argument("--format", choices=("text", "json"), default="text")
    agent_parser.add_argument("--artifacts-dir", type=Path, default=Path("artifacts/runs"))
    agent_parser.add_argument("--timeout-seconds", type=int, default=600)
    agent_parser.add_argument("--max-attempts", type=int, default=1)
    agent_parser.add_argument("--max-tool-calls", type=int, default=50)
    agent_parser.add_argument("--max-tokens", type=int, default=100000)
    agent_parser.add_argument("--max-cost-usd", type=float, default=10.0)
    reviewer_parser = subcommands.add_parser("review-evaluate")
    reviewer_parser.add_argument("--task", required=True, type=Path)
    reviewer_parser.add_argument("--patch", required=True, type=Path)
    reviewer_parser.add_argument("--format", choices=("text", "json"), default="text")
    reviewer_parser.add_argument("--artifacts-dir", type=Path, default=Path("artifacts/reviews"))
    reviewer_parser.add_argument("--timeout-seconds", type=int, default=600)
    reviewer_parser.add_argument("--max-tool-calls", type=int, default=50)
    reviewer_parser.add_argument("--max-tokens", type=int, default=100000)
    reviewer_parser.add_argument("--max-cost-usd", type=float, default=10.0)
    show_parser = subcommands.add_parser("show")
    show_parser.add_argument("run_id")
    show_parser.add_argument("--format", choices=("text", "json"), default="text")
    show_parser.add_argument("--artifacts-dir", type=Path, default=Path("artifacts/runs"))
    replay_parser = subcommands.add_parser("replay")
    replay_parser.add_argument("run_id")
    replay_parser.add_argument("--format", choices=("text", "json"), default="text")
    replay_parser.add_argument("--artifacts-dir", type=Path, default=Path("artifacts/runs"))
    report_parser = subcommands.add_parser("report")
    report_parser.add_argument("--format", choices=("text", "json"), default="text")
    report_parser.add_argument("--artifacts-dir", type=Path, default=Path("artifacts/runs"))
    review_report_parser = subcommands.add_parser("review-report")
    review_report_parser.add_argument("--format", choices=("text", "json"), default="text")
    review_report_parser.add_argument("--artifacts-dir", type=Path, default=Path("artifacts/reviews"))
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

    if arguments.command == "report":
        report = build_report([stored_run.payload for stored_run in run_store.list_runs()])
        print(json.dumps(report, sort_keys=True) if arguments.format == "json" else json.dumps(report, indent=2, sort_keys=True))
        return 0

    if arguments.command == "review-report":
        try:
            report = build_review_report(list(FilesystemReviewStore(arguments.artifacts_dir).list_reviews()))
        except ReviewStoreError as error:
            parser.error(str(error))
        print(json.dumps(report, sort_keys=True) if arguments.format == "json" else json.dumps(report, indent=2, sort_keys=True))
        return 0

    try:
        task = load_task(arguments.task)
    except TaskValidationError as error:
        parser.error(str(error))

    if arguments.command == "review-evaluate":
        budget = ReviewerBudget(
            timeout_seconds=arguments.timeout_seconds,
            max_tool_calls=arguments.max_tool_calls,
            max_tokens=arguments.max_tokens,
            max_cost_usd=arguments.max_cost_usd,
        )
        try:
            candidate_kind = _candidate_kind(task, arguments.patch)
            with tempfile.TemporaryDirectory(prefix="patchbench-review-output-") as temporary_directory:
                attempt = CommandReviewerAdapter.from_environment().review(task, arguments.patch, Path(temporary_directory), budget)
            result = ReviewResult(task, arguments.patch, score_finding(task, attempt.finding, candidate_kind), attempt.finding, attempt.duration_seconds, candidate_kind)
        except (ReviewerConfigurationError, ReviewerExecutionError, ValueError) as error:
            result = ReviewResult(
                task,
                arguments.patch,
                ReviewScore(ReviewClassification.INCONCLUSIVE, str(error)),
                None,
                None,
            )
        result = FilesystemReviewStore(arguments.artifacts_dir).save(result)
        print(render_review_json(result) if arguments.format == "json" else render_review_text(result))
        return 3 if result.score.classification is ReviewClassification.INCONCLUSIVE else 0
    if arguments.command == "verify-working-tree":
        result = _evaluate_working_tree(task, run_store)
    elif arguments.command == "codex-run":
        try:
            run_codex(task.repository, arguments.prompt)
        except CodexRunError as error:
            result = EvaluationResult(
                classification=Classification.INCONCLUSIVE,
                task=task,
                patch=Path("codex-output.patch"),
                checks=(),
                reason=str(error),
            )
        else:
            result = _evaluate_working_tree(task, run_store)
        if result.run_id is None:
            result = run_store.save(result)
    elif arguments.command == "agent-evaluate":
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


def _evaluate_working_tree(task, run_store):
    with tempfile.TemporaryDirectory(prefix="patchbench-working-tree-") as temporary_directory:
        patch = Path(temporary_directory) / "candidate.patch"
        try:
            write_working_tree_patch(task.repository, patch)
        except WorkingTreeError as error:
            return EvaluationResult(
                classification=Classification.INCONCLUSIVE,
                task=task,
                patch=patch,
                checks=(),
                reason=str(error),
            )
        return run_store.save(evaluate(task, patch))


def _candidate_kind(task, patch: Path):
    patch_path = patch.resolve()
    for candidate in task.candidates:
        if candidate.patch.resolve() == patch_path:
            return candidate.kind
    raise ValueError(f"patch is not a registered candidate: {patch}")


if __name__ == "__main__":
    raise SystemExit(main())
