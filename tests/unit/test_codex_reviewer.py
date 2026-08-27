import os
import stat
import sys
from pathlib import Path

from patchbench.models import ReviewClassification
from patchbench.review_scoring import score_finding
from patchbench.reviewers import CommandReviewerAdapter, ReviewerBudget
from patchbench.task_loader import load_task


def test_codex_reviewer_writes_schema_output(tmp_path, monkeypatch):
    codex = tmp_path / "codex"
    codex.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json",
                "import sys",
                "from pathlib import Path",
                "output = Path(sys.argv[sys.argv.index('-o') + 1])",
                "output.write_text(json.dumps({'outcome': 'finding', 'category': 'preservation', 'affected_paths': ['user_store.py'], 'affected_symbols': ['UserStore.delete_user'], 'rationale': 'Deletion does not evict the cached user.'}))",
            ]
        )
        + "\n"
    )
    codex.chmod(codex.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ['PATH']}")
    task = load_task(Path("fixtures/cache-invalidation"))
    script = Path("scripts/patchbench_codex_reviewer.py").resolve()

    attempt = CommandReviewerAdapter((sys.executable, str(script))).review(
        task,
        Path("fixtures/cache-invalidation/candidates/stale-cache.patch"),
        tmp_path / "output",
        ReviewerBudget(10, 5, 1000, 1.0),
    )

    assert attempt.finding is not None
    assert score_finding(task, attempt.finding).classification is ReviewClassification.DETECTED


def test_codex_reviewer_translates_no_finding(tmp_path, monkeypatch):
    codex = tmp_path / "codex"
    codex.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json",
                "import sys",
                "from pathlib import Path",
                "output = Path(sys.argv[sys.argv.index('-o') + 1])",
                "output.write_text(json.dumps({'outcome': 'no_finding', 'category': 'none', 'affected_paths': [], 'affected_symbols': [], 'rationale': ''}))",
            ]
        )
        + "\n"
    )
    codex.chmod(codex.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ['PATH']}")

    attempt = CommandReviewerAdapter((sys.executable, str(Path("scripts/patchbench_codex_reviewer.py").resolve()))).review(
        load_task(Path("fixtures/cache-invalidation")),
        Path("fixtures/cache-invalidation/candidates/stale-cache.patch"),
        tmp_path / "output",
        ReviewerBudget(10, 5, 1000, 1.0),
    )

    assert attempt.finding is None
