from dataclasses import replace
from pathlib import Path

import pytest

from patchbench.models import ReviewClassification, ReviewerFinding
from patchbench.review_scoring import score_finding
from patchbench.task_loader import load_task


def test_scores_matching_finding_as_detected():
    task = load_task(Path("fixtures/cache-invalidation"))
    score = score_finding(
        task,
        ReviewerFinding(
            category="preservation",
            affected_paths=("user_store.py",),
            affected_symbols=("UserStore.delete_user",),
            rationale="Deleting a user leaves a cached record available.",
        ),
    )

    assert score.classification is ReviewClassification.DETECTED
    assert score.reason == "finding matches ground-truth path"


def test_scores_no_finding_as_missed():
    score = score_finding(load_task(Path("fixtures/cache-invalidation")), None)

    assert score.classification is ReviewClassification.MISSED
    assert score.reason == "reviewer reported no finding"


def test_scores_unrelated_finding_as_false_positive():
    score = score_finding(
        load_task(Path("fixtures/cache-invalidation")),
        ReviewerFinding(
            category="safety",
            affected_paths=("user_store.py",),
            affected_symbols=("UserStore.get_user",),
            rationale="The read path exposes sensitive data.",
        ),
    )

    assert score.classification is ReviewClassification.FALSE_POSITIVE
    assert score.reason == "finding category does not match ground truth"


def test_scores_wrong_evidence_as_false_positive():
    score = score_finding(
        load_task(Path("fixtures/cache-invalidation")),
        ReviewerFinding(
            category="preservation",
            affected_paths=("other.py",),
            affected_symbols=("OtherStore.delete",),
            rationale="An unrelated deletion path changes behavior.",
        ),
    )

    assert score.classification is ReviewClassification.FALSE_POSITIVE
    assert score.reason == "finding evidence does not match ground truth"


def test_rejects_scoring_task_without_ground_truth():
    task = load_task(Path("fixtures/cache-invalidation"))

    with pytest.raises(ValueError, match="task has no reviewer ground truth"):
        score_finding(replace(task, reviewer_ground_truth=None), None)
