import json
import sys

from patchbench.cli import main


def test_review_evaluate_scores_and_stores_finding(tmp_path, monkeypatch, capsys):
    script = tmp_path / "reviewer.py"
    script.write_text(
        "\n".join(
            [
                "import json",
                "import os",
                "from pathlib import Path",
                "Path(os.environ['PATCHBENCH_REVIEWER_OUTPUT']).write_text(json.dumps({'category': 'preservation', 'affected_paths': ['user_store.py'], 'affected_symbols': [], 'rationale': 'Cached users remain readable after deletion.'}))",
            ]
        )
        + "\n"
    )
    monkeypatch.setenv("PATCHBENCH_REVIEWER_COMMAND", f"{sys.executable} {script}")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "patchbench",
            "review-evaluate",
            "--task",
            "fixtures/cache-invalidation",
            "--patch",
            "fixtures/cache-invalidation/candidates/stale-cache.patch",
            "--artifacts-dir",
            str(tmp_path / "reviews"),
            "--format",
            "json",
        ],
    )

    assert main() == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["score"] == "DETECTED"
    assert payload["candidate_kind"] == "known_regression"
    assert (tmp_path / "reviews" / payload["review_id"] / "result.json").is_file()


def test_review_report_aggregates_stored_reviews(tmp_path, monkeypatch, capsys):
    reviews = tmp_path / "reviews"
    review = reviews / "review-1"
    review.mkdir(parents=True)
    (review / "result.json").write_text(
        json.dumps(
            {
                "review_id": "review-1",
                "task": {"id": "cache-invalidation-v1", "version": 1},
                "candidate_kind": "known_regression",
                "score": "DETECTED",
                "reason": "finding matches ground-truth symbol",
                "finding": None,
                "duration_seconds": 3.0,
                "created_at": "2026-08-28T00:00:00+00:00",
            }
        )
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["patchbench", "review-report", "--artifacts-dir", str(reviews), "--format", "json"],
    )

    assert main() == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["reviews"]["detection_rate"] == 1.0
    assert payload["tasks"]["cache-invalidation-v1@1"]["total_reviews"] == 1
