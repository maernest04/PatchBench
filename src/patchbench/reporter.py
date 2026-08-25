import json

from patchbench.models import EvaluationResult


def render_text(result: EvaluationResult) -> str:
    lines = [result.classification, f"Task: {result.task.identifier}@{result.task.version}"]
    for check_result in result.checks:
        status = "PASS" if check_result.command.returncode == 0 else "FAIL"
        lines.append(f"{status} {check_result.check.visibility} check: {check_result.check.name}")
    if result.reason:
        lines.append(f"Reason: {result.reason}")
    return "\n".join(lines)


def render_json(result: EvaluationResult) -> str:
    payload = {
        "classification": result.classification,
        "task": {"id": result.task.identifier, "version": result.task.version},
        "patch": str(result.patch),
        "reason": result.reason,
        "checks": [
            {
                "name": check_result.check.name,
                "visibility": check_result.check.visibility,
                "returncode": check_result.command.returncode,
                "duration_seconds": check_result.command.duration_seconds,
            }
            for check_result in result.checks
        ],
    }
    return json.dumps(payload, sort_keys=True)
