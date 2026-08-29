from collections import Counter


REPORT_VERSION = 1
REVIEW_REPORT_VERSION = 1


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


def build_review_report(payloads: list[dict]) -> dict:
    by_task = {}
    for payload in payloads:
        task = payload["task"]
        key = f"{task['id']}@{task['version']}"
        by_task.setdefault(key, []).append(payload)
    return {
        "review_report_version": REVIEW_REPORT_VERSION,
        "reviews": _review_summary(payloads),
        "tasks": {key: _review_summary(task_payloads) for key, task_payloads in by_task.items()},
        "attempts": [_review_attempt(payload) for payload in payloads],
        "limitations": [
            "Rates describe only stored reviewer attempts and are not a general model ranking.",
            "Unlabeled historical review records are excluded from control and known-regression rates.",
        ],
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


def _review_summary(payloads: list[dict]) -> dict:
    scores = Counter(payload["score"] for payload in payloads)
    total = len(payloads)
    durations = [payload["duration_seconds"] for payload in payloads if payload["duration_seconds"] is not None]
    return {
        "total_reviews": total,
        "outcomes": dict(scores),
        "known_regression_reviews": len([payload for payload in payloads if payload.get("candidate_kind") == "known_regression"]),
        "control_reviews": len([payload for payload in payloads if payload.get("candidate_kind") == "control"]),
        "unlabeled_reviews": len([payload for payload in payloads if payload.get("candidate_kind") is None]),
        "detection_rate": _review_rate(payloads, "known_regression", "DETECTED"),
        "miss_rate": _review_rate(payloads, "known_regression", "MISSED"),
        "false_positive_rate": _review_rate(payloads, "control", "FALSE_POSITIVE"),
        "correct_rejection_rate": _review_rate(payloads, "control", "CORRECT_REJECTION"),
        "inconclusive_rate": _rate(scores["INCONCLUSIVE"], total),
        "average_duration_seconds": sum(durations) / len(durations) if durations else None,
    }


def _review_attempt(payload: dict) -> dict:
    return {
        "review_id": payload["review_id"],
        "task": payload["task"],
        "candidate_kind": payload.get("candidate_kind"),
        "score": payload["score"],
        "reason": payload["reason"],
        "finding": payload["finding"],
        "duration_seconds": payload["duration_seconds"],
        "created_at": payload["created_at"],
    }


def _review_rate(payloads: list[dict], candidate_kind: str, score: str) -> float:
    matching = [payload for payload in payloads if payload.get("candidate_kind") == candidate_kind]
    return _rate(sum(payload["score"] == score for payload in matching), len(matching))


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
