import argparse
from pathlib import Path

from patchbench.models import Classification
from patchbench.evaluator import evaluate
from patchbench.reporter import render_json, render_text
from patchbench.task_loader import TaskValidationError, load_task


def main() -> int:
    parser = argparse.ArgumentParser(prog="patchbench")
    subcommands = parser.add_subparsers(dest="command", required=True)
    evaluate_parser = subcommands.add_parser("evaluate")
    evaluate_parser.add_argument("--task", required=True, type=Path)
    evaluate_parser.add_argument("--patch", required=True, type=Path)
    evaluate_parser.add_argument("--format", choices=("text", "json"), default="text")
    arguments = parser.parse_args()

    if arguments.command != "evaluate":
        return 2

    try:
        task = load_task(arguments.task)
    except TaskValidationError as error:
        parser.error(str(error))

    result = evaluate(task, arguments.patch)
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
