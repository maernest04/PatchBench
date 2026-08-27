from patchbench.models import ReviewClassification, ReviewerFinding, ReviewScore, Task


def score_finding(task: Task, finding: ReviewerFinding | None) -> ReviewScore:
    ground_truth = task.reviewer_ground_truth
    if ground_truth is None:
        raise ValueError(f"task has no reviewer ground truth: {task.identifier}")
    if finding is None:
        return ReviewScore(classification=ReviewClassification.MISSED, reason="reviewer reported no finding")
    if finding.category != ground_truth.category:
        return ReviewScore(classification=ReviewClassification.FALSE_POSITIVE, reason="finding category does not match ground truth")
    if set(finding.affected_paths) & set(ground_truth.affected_paths):
        return ReviewScore(classification=ReviewClassification.DETECTED, reason="finding matches ground-truth path")
    if set(finding.affected_symbols) & set(ground_truth.affected_symbols):
        return ReviewScore(classification=ReviewClassification.DETECTED, reason="finding matches ground-truth symbol")
    return ReviewScore(classification=ReviewClassification.FALSE_POSITIVE, reason="finding evidence does not match ground truth")
