import argparse
import json
from pathlib import Path

from patchbench.models import Classification
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
