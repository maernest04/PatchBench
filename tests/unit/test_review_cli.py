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
    assert (tmp_path / "reviews" / payload["review_id"] / "result.json").is_file()
