from patchbench.benchmark import build_report


def test_reports_classifications_safety_and_reproducibility_separately():
    payloads = [
        {
            "run_id": "run-1",
            "replay_of": None,
            "classification": "PASS",
            "task": {"id": "task", "version": 1},
            "agent": {"adapter": "command"},
            "checks": [{"visibility": "public", "category": "correctness", "returncode": 0, "duration_seconds": 1.0}],
        },
        {
            "run_id": "run-2",
            "replay_of": None,
            "classification": "FAIL",
            "task": {"id": "task", "version": 1},
            "agent": None,
            "checks": [{"visibility": "hidden", "category": "safety", "returncode": 1, "duration_seconds": 3.0}],
        },
        {
            "run_id": "run-3",
            "replay_of": "run-1",
            "classification": "PASS",
            "task": {"id": "task", "version": 1},
            "agent": None,
            "checks": [{"visibility": "hidden", "category": "correctness", "returncode": 0, "duration_seconds": 2.0}],
        },
    ]

    report = build_report(payloads)

    summary = report["runs"]
    assert summary["task_success_rate"] == 1 / 2
    assert summary["hidden_failure_rate"] == 1 / 2
    assert summary["safety_violation_rate"] == 1 / 2
    assert summary["inconclusive_rate"] == 0.0
    assert summary["average_check_duration_seconds"] == 2.0
    assert summary["reproducibility_rate"] == 1.0
    assert summary["sources"] == {"agent": 1, "fixture": 1}
