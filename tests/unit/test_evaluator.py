from pathlib import Path

from patchbench.evaluator import evaluate
from patchbench.models import CommandResult, Classification
from patchbench.task_loader import load_task


class FixtureRunner:
    def run_check(self, task, workspace, check):
        source = (workspace / "user_store.py").read_text()
        stale_cache = "def delete_user(self, user_id):\n        return self._users.pop" in source
        return CommandResult(
            returncode=1 if check.visibility == "hidden" and stale_cache else 0,
            stdout="",
            stderr="hidden regression" if stale_cache else "",
            duration_seconds=0.0,
        )

    def run_differential(self, task, baseline, workspace, check):
        source = (workspace / "user_store.py").read_text()
        stale_cache = "def delete_user(self, user_id):\n        return self._users.pop" in source
        return CommandResult(
            returncode=1 if stale_cache else 0,
            stdout="",
            stderr="baseline and candidate behavior differ" if stale_cache else "",
            duration_seconds=0.0,
        )


def test_correct_candidate_passes():
    fixture = Path("fixtures/cache-invalidation")
    result = evaluate(
        load_task(fixture),
        fixture / "candidates" / "correct.patch",
        runner=FixtureRunner(),
    )

    assert result.classification is Classification.PASS


def test_stale_cache_candidate_fails_hidden_check():
    fixture = Path("fixtures/cache-invalidation")
    result = evaluate(
        load_task(fixture),
        fixture / "candidates" / "stale-cache.patch",
        runner=FixtureRunner(),
    )

    assert result.classification is Classification.FAIL
    assert result.reason == "hidden check failed: deleted-users-are-not-readable"
