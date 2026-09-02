from dataclasses import replace
from pathlib import Path

import pytest

from patchbench.models import CandidateKind, ReviewClassification, ReviewerFinding
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
        CandidateKind.KNOWN_REGRESSION,
    )

    assert score.classification is ReviewClassification.DETECTED
    assert score.reason == "finding matches ground-truth path"


@pytest.mark.parametrize(
    ("fixture_name", "category", "path", "symbol"),
    [
        ("cli-report-generation", "correctness", "report.py", "main"),
        ("api-user-directory", "preservation", "user_directory.py", "UserDirectory.lookup"),
        ("refactor-pricing", "preservation", "pricing.py", "calculate_total"),
        ("redacted-audit-log", "safety", "audit.py", "format_login_event"),
        ("retry-delivery", "reliability", "delivery.py", "DeliveryService.deliver"),
    ],
)
def test_scores_pilot_fixture_finding_as_detected(fixture_name, category, path, symbol):
    score = score_finding(
        load_task(Path("fixtures") / fixture_name),
        ReviewerFinding(
            category=category,
            affected_paths=(path,),
            affected_symbols=(symbol,),
            rationale="The candidate changes required behavior.",
        ),
        CandidateKind.KNOWN_REGRESSION,
    )

    assert score.classification is ReviewClassification.DETECTED


def test_scores_no_finding_as_missed():
    score = score_finding(load_task(Path("fixtures/cache-invalidation")), None, CandidateKind.KNOWN_REGRESSION)

    assert score.classification is ReviewClassification.MISSED
    assert score.reason == "reviewer reported no finding"


@pytest.mark.parametrize(
    "fixture_name",
    (
        "api-user-directory",
        "cache-invalidation",
        "cli-report-generation",
        "redacted-audit-log",
        "refactor-pricing",
        "retry-delivery",
    ),
)
def test_scores_unrelated_finding_as_false_positive(fixture_name):
    score = score_finding(
        load_task(Path("fixtures") / fixture_name),
        ReviewerFinding(
            category="efficiency",
            affected_paths=("unrelated.py",),
            affected_symbols=("unrelated",),
            rationale="The candidate causes an unrelated performance regression.",
        ),
        CandidateKind.KNOWN_REGRESSION,
    )

    assert score.classification is ReviewClassification.FALSE_POSITIVE


def test_scores_matching_symbol_as_detected_despite_category_difference():
    score = score_finding(
        load_task(Path("fixtures/cache-invalidation")),
        ReviewerFinding(
            category="correctness",
            affected_paths=("user_store.py",),
            affected_symbols=("UserStore.delete_user",),
            rationale="The delete path leaves stale cache entries available.",
        ),
        CandidateKind.KNOWN_REGRESSION,
    )

    assert score.classification is ReviewClassification.DETECTED
    assert score.reason == "finding matches ground-truth symbol"


def test_scores_wrong_evidence_as_false_positive():
    score = score_finding(
        load_task(Path("fixtures/cache-invalidation")),
        ReviewerFinding(
            category="preservation",
            affected_paths=("other.py",),
            affected_symbols=("OtherStore.delete",),
            rationale="An unrelated deletion path changes behavior.",
        ),
        CandidateKind.KNOWN_REGRESSION,
    )

    assert score.classification is ReviewClassification.FALSE_POSITIVE
    assert score.reason == "finding evidence does not match ground truth"


def test_rejects_scoring_task_without_ground_truth():
    task = load_task(Path("fixtures/cache-invalidation"))

    with pytest.raises(ValueError, match="task has no reviewer ground truth"):
        score_finding(replace(task, reviewer_ground_truth=None), None, CandidateKind.KNOWN_REGRESSION)


def test_scores_control_without_finding_as_correct_rejection():
    score = score_finding(load_task(Path("fixtures/cache-invalidation")), None, CandidateKind.CONTROL)

    assert score.classification is ReviewClassification.CORRECT_REJECTION


def test_scores_control_finding_as_false_positive():
    score = score_finding(
        load_task(Path("fixtures/cache-invalidation")),
        ReviewerFinding("correctness", ("user_store.py",), (), "The change is unsafe."),
        CandidateKind.CONTROL,
    )

    assert score.classification is ReviewClassification.FALSE_POSITIVE
