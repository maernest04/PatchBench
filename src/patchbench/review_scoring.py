from patchbench.models import ArtifactValidation, CandidateKind, ReviewClassification, ReviewerFinding, ReviewScore, Task


def score_finding(
    task: Task,
    finding: ReviewerFinding | None,
    candidate_kind: CandidateKind,
    artifact_validation: ArtifactValidation | None = None,
) -> ReviewScore:
    if candidate_kind is CandidateKind.CONTROL:
        if finding is None:
            return ReviewScore(classification=ReviewClassification.CORRECT_REJECTION, reason="reviewer reported no finding for control")
        return ReviewScore(classification=ReviewClassification.FALSE_POSITIVE, reason="reviewer reported a finding for control")
    ground_truth = task.reviewer_ground_truth
    if ground_truth is None:
        raise ValueError(f"task has no reviewer ground truth: {task.identifier}")
    if finding is None:
        return ReviewScore(classification=ReviewClassification.MISSED, reason="reviewer reported no finding")
    matching_paths = set(finding.affected_paths) & set(ground_truth.affected_paths)
    matching_symbols = set(finding.affected_symbols) & set(ground_truth.affected_symbols)
    if finding.category == ground_truth.category and matching_paths:
        if artifact_validation and artifact_validation.passed:
            return ReviewScore(classification=ReviewClassification.EXECUTABLE_DETECTED, reason=artifact_validation.reason)
        return ReviewScore(classification=ReviewClassification.DETECTED, reason="finding matches ground-truth path")
    if matching_symbols:
        if artifact_validation and artifact_validation.passed:
            return ReviewScore(classification=ReviewClassification.EXECUTABLE_DETECTED, reason=artifact_validation.reason)
        return ReviewScore(classification=ReviewClassification.DETECTED, reason="finding matches ground-truth symbol")
    if finding.category != ground_truth.category:
        return ReviewScore(classification=ReviewClassification.FALSE_POSITIVE, reason="finding category does not match ground truth")
    return ReviewScore(classification=ReviewClassification.FALSE_POSITIVE, reason="finding evidence does not match ground truth")
