import json

from patchbench.models import EvaluationResult, ReviewResult


def render_text(result: EvaluationResult) -> str:
    lines = [result.classification, f"Task: {result.task.identifier}@{result.task.version}"]
    if result.run_id:
        lines.append(f"Run: {result.run_id}")
    if result.replay_of:
        lines.append(f"Replay of: {result.replay_of}")
    if result.agent:
        lines.append(f"Agent: {result.agent.adapter}")
        lines.append(f"Agent duration: {result.agent.duration_seconds}")
    for check_result in result.checks:
        status = "PASS" if check_result.command.returncode == 0 else "FAIL"
        lines.append(f"{status} {check_result.check.visibility} check: {check_result.check.name}")
        if check_result.check.kind == "differential" and check_result.command.returncode != 0:
            try:
                evidence = json.loads(check_result.command.stdout)
                lines.append(f"Baseline output: {evidence['baseline']['normalized_stdout']}")
                lines.append(f"Candidate output: {evidence['candidate']['normalized_stdout']}")
            except (json.JSONDecodeError, KeyError):
                pass
    if result.reason:
        lines.append(f"Reason: {result.reason}")
    return "\n".join(lines)


def render_json(result: EvaluationResult) -> str:
    return json.dumps(result_payload(result), sort_keys=True)


def result_payload(result: EvaluationResult) -> dict:
    return {
        "classification": result.classification,
        "run_id": result.run_id,
        "replay_of": result.replay_of,
        "task": {"id": result.task.identifier, "version": result.task.version},
        "patch": str(result.patch),
        "reason": result.reason,
        "agent": _agent_payload(result.agent),
        "checks": [
            {
                "name": check_result.check.name,
                "visibility": check_result.check.visibility,
                "category": check_result.check.category,
                "returncode": check_result.command.returncode,
                "duration_seconds": check_result.command.duration_seconds,
            }
            for check_result in result.checks
        ],
    }


def _agent_payload(agent):
    if agent is None:
        return None
    return {
        "adapter": agent.adapter,
        "duration_seconds": agent.duration_seconds,
        "attempts": agent.attempts,
        "budget": {
            "max_attempts": agent.max_attempts,
            "max_tool_calls": agent.max_tool_calls,
            "max_tokens": agent.max_tokens,
            "max_cost_usd": agent.max_cost_usd,
        },
    }


def render_stored_text(payload: dict) -> str:
    lines = [payload["classification"], f"Task: {payload['task']['id']}@{payload['task']['version']}"]
    if payload.get("run_id"):
        lines.append(f"Run: {payload['run_id']}")
    if payload.get("replay_of"):
        lines.append(f"Replay of: {payload['replay_of']}")
    for check in payload["checks"]:
        status = "PASS" if check["returncode"] == 0 else "FAIL"
        lines.append(f"{status} {check['visibility']} check: {check['name']}")
    if payload.get("reason"):
        lines.append(f"Reason: {payload['reason']}")
    return "\n".join(lines)


def render_review_text(result: ReviewResult) -> str:
    lines = [result.score.classification, f"Task: {result.task.identifier}@{result.task.version}"]
    if result.review_id:
        lines.append(f"Review: {result.review_id}")
    lines.append(f"Reason: {result.score.reason}")
    return "\n".join(lines)


def render_review_json(result: ReviewResult) -> str:
    return json.dumps(
        {
            "review_id": result.review_id,
            "task": {"id": result.task.identifier, "version": result.task.version},
            "candidate_kind": result.candidate_kind,
            "score": result.score.classification,
            "reason": result.score.reason,
            "finding": None
            if result.finding is None
            else {
                "category": result.finding.category,
                "affected_paths": result.finding.affected_paths,
                "affected_symbols": result.finding.affected_symbols,
                "rationale": result.finding.rationale,
            },
            "duration_seconds": result.duration_seconds,
        },
        sort_keys=True,
    )
