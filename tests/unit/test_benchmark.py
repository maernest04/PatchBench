from patchbench.benchmark import build_report, build_review_report


def test_reports_classifications_safety_and_reproducibility_separately():
    payloads = [
        {
            "run_id": "run-1",
            "replay_of": None,
            "classification": "PASS",
            "task": {"id": "task", "version": 1},
            "candidate_kind": "known_regression",
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


def test_reports_reviewer_outcomes_by_task_and_attempt():
    payloads = [
        {
            "review_id": "review-1",
            "task": {"id": "task", "version": 1},
            "candidate_kind": "known_regression",
            "score": "DETECTED",
            "reason": "matching symbol",
            "finding": {"category": "correctness"},
            "duration_seconds": 2.0,
            "created_at": "2026-08-28T00:00:00+00:00",
        },
        {
            "review_id": "review-2",
            "task": {"id": "other", "version": 1},
            "candidate_kind": "control",
            "score": "CORRECT_REJECTION",
            "reason": "no finding",
            "finding": None,
            "duration_seconds": None,
            "created_at": "2026-08-28T00:01:00+00:00",
        },
    ]

    report = build_review_report(payloads)

    assert report["reviews"]["total_reviews"] == 2
    assert report["reviews"]["outcomes"] == {"DETECTED": 1, "CORRECT_REJECTION": 1}
    assert report["reviews"]["detection_rate"] == 1.0
    assert report["reviews"]["correct_rejection_rate"] == 1.0
    assert report["reviews"]["average_duration_seconds"] == 2.0
    assert report["tasks"]["task@1"]["detection_rate"] == 1.0
    assert report["attempts"][0]["review_id"] == "review-1"
