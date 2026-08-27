import json
import sys
from pathlib import Path

import pytest

from patchbench.models import ReviewClassification
from patchbench.review_scoring import score_finding
from patchbench.reviewers import CommandReviewerAdapter, ReviewerBudget, ReviewerExecutionError
from patchbench.task_loader import load_task


def test_reviewer_receives_only_public_material(tmp_path):
    script = tmp_path / "reviewer.py"
    script.write_text(
        "\n".join(
            [
                "import json",
                "import os",
                "from pathlib import Path",
                "repository = Path(os.environ['PATCHBENCH_REVIEWER_REPOSITORY'])",
                "public = Path(os.environ['PATCHBENCH_REVIEWER_PUBLIC_DIR'])",
                "assert (repository / 'user_store.py').is_file()",
                "assert (public / 'task.md').is_file()",
                "assert Path(os.environ['PATCHBENCH_REVIEWER_PATCH']).is_file()",
                "assert not (repository.parent / 'hidden').exists()",
                "Path(os.environ['PATCHBENCH_REVIEWER_OUTPUT']).write_text(json.dumps({'category': 'preservation', 'affected_paths': ['user_store.py'], 'affected_symbols': [], 'rationale': 'Cached users remain readable after deletion.'}))",
            ]
        )
        + "\n"
    )
    task = load_task(Path("fixtures/cache-invalidation"))
    attempt = CommandReviewerAdapter((sys.executable, str(script))).review(
        task,
        Path("fixtures/cache-invalidation/candidates/stale-cache.patch"),
        tmp_path / "output",
        ReviewerBudget(10, 5, 1000, 1.0),
    )

    assert attempt.finding is not None
    assert score_finding(task, attempt.finding).classification is ReviewClassification.DETECTED


def test_reviewer_can_report_no_finding(tmp_path):
    script = tmp_path / "reviewer.py"
    script.write_text(
        "\n".join(
            [
                "import os",
                "from pathlib import Path",
                "Path(os.environ['PATCHBENCH_REVIEWER_OUTPUT']).write_text('null')",
            ]
        )
        + "\n"
    )
    attempt = CommandReviewerAdapter((sys.executable, str(script))).review(
        load_task(Path("fixtures/cache-invalidation")),
        Path("fixtures/cache-invalidation/candidates/stale-cache.patch"),
        tmp_path / "output",
        ReviewerBudget(10, 5, 1000, 1.0),
    )

    assert attempt.finding is None


def test_reviewer_rejects_malformed_json(tmp_path):
    script = tmp_path / "reviewer.py"
    script.write_text(
        "\n".join(
            [
                "import os",
                "from pathlib import Path",
                "Path(os.environ['PATCHBENCH_REVIEWER_OUTPUT']).write_text('{')",
            ]
        )
        + "\n"
    )

    with pytest.raises(ReviewerExecutionError, match="reviewer output is not valid JSON"):
        CommandReviewerAdapter((sys.executable, str(script))).review(
            load_task(Path("fixtures/cache-invalidation")),
            Path("fixtures/cache-invalidation/candidates/stale-cache.patch"),
            tmp_path / "output",
            ReviewerBudget(10, 5, 1000, 1.0),
        )
