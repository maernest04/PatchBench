from collections import Counter


REPORT_VERSION = 1


def build_report(payloads: list[dict]) -> dict:
    by_task = {}
    for payload in payloads:
        task = payload["task"]
        key = f"{task['id']}@{task['version']}"
        by_task.setdefault(key, []).append(payload)
    return {
        "report_version": REPORT_VERSION,
        "runs": _summary(payloads),
        "tasks": {key: _summary(task_payloads) for key, task_payloads in by_task.items()},
        "limitations": _limitations(payloads),
    }


def _summary(payloads: list[dict]) -> dict:
    run_by_id = {payload.get("run_id"): payload for payload in payloads}
    attempts = [payload for payload in payloads if not payload.get("replay_of")]
    total = len(attempts)
    classifications = Counter(payload["classification"] for payload in attempts)
    hidden_failures = sum(_has_failed_check(payload, visibility="hidden") for payload in attempts)
    safety_violations = sum(_has_failed_check(payload, category="safety") for payload in attempts)
    durations = [check["duration_seconds"] for payload in attempts for check in payload["checks"]]
    replays = [payload for payload in payloads if payload.get("replay_of") in run_by_id]
    reproducible = sum(
        payload["classification"] == run_by_id[payload["replay_of"]]["classification"] for payload in replays
    )
    sources = Counter(_source(payload, run_by_id) for payload in attempts)
    return {
        "total_runs": total,
        "sources": dict(sources),
        "task_success_rate": _rate(classifications["PASS"], total),
        "hidden_failure_rate": _rate(hidden_failures, total),
        "safety_violation_rate": _rate(safety_violations, total),
        "inconclusive_rate": _rate(classifications["INCONCLUSIVE"], total),
        "average_check_duration_seconds": sum(durations) / len(durations) if durations else None,
        "reproducibility_rate": _rate(reproducible, len(replays)) if replays else None,
        "replay_count": len(replays),
    }


def _has_failed_check(payload: dict, visibility: str | None = None, category: str | None = None) -> bool:
    return any(
        check["returncode"] != 0
        and (visibility is None or check["visibility"] == visibility)
        and (category is None or check.get("category", "correctness") == category)
        for check in payload["checks"]
    )


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _source(payload: dict, run_by_id: dict[str, dict]) -> str:
    if payload.get("agent"):
        return "agent"
    if payload.get("replay_of") in run_by_id:
        return _source(run_by_id[payload["replay_of"]], run_by_id)
    return "fixture"


def _limitations(payloads: list[dict]) -> list[str]:
    limitations = ["Rates describe only stored runs and are not a general model ranking."]
    if not any(payload.get("agent") for payload in payloads):
        limitations.append("No real-agent attempts are included.")
    if not any(payload.get("replay_of") for payload in payloads):
        limitations.append("No replay pairs are included.")
    return limitations
