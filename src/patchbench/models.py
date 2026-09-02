from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class Classification(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    INCONCLUSIVE = "INCONCLUSIVE"


class ReviewClassification(StrEnum):
    DETECTED = "DETECTED"
    MISSED = "MISSED"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    CORRECT_REJECTION = "CORRECT_REJECTION"
    INCONCLUSIVE = "INCONCLUSIVE"


class CandidateKind(StrEnum):
    CONTROL = "control"
    KNOWN_REGRESSION = "known_regression"


@dataclass(frozen=True)
class Constraints:
    timeout_seconds: int
    memory_megabytes: int
    cpu_cores: float


@dataclass(frozen=True)
class Check:
    name: str
    kind: str
    visibility: str
    path: Path | None = None
    command: tuple[str, ...] = ()
    expected_exit_code: int = 0
    expected_stdout: str = ""
    expected_files: tuple[tuple[str, str], ...] = ()
    category: str = "correctness"


@dataclass(frozen=True)
class Task:
    identifier: str
    version: int
    root: Path
    repository: Path
    image: str
    dockerfile: Path | None
    constraints: Constraints
    checks: tuple[Check, ...]
    candidates: tuple["Candidate", ...] = ()
    reviewer_ground_truth: "ReviewerGroundTruth | None" = None


@dataclass(frozen=True)
class Candidate:
    patch: Path
    kind: CandidateKind


@dataclass(frozen=True)
class ReviewerGroundTruth:
    fault_id: str
    category: str
    affected_paths: tuple[str, ...]
    affected_symbols: tuple[str, ...]


@dataclass(frozen=True)
class ReviewerFinding:
    category: str
    affected_paths: tuple[str, ...]
    affected_symbols: tuple[str, ...]
    rationale: str


@dataclass(frozen=True)
class ReviewScore:
    classification: ReviewClassification
    reason: str


@dataclass(frozen=True)
class ReviewResult:
    task: Task
    patch: Path
    score: ReviewScore
    finding: ReviewerFinding | None
    duration_seconds: float | None
    candidate_kind: CandidateKind | None = None
    experiment_id: str | None = None
    attempt_number: int | None = None
    review_id: str | None = None


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str
    duration_seconds: float


@dataclass(frozen=True)
class CheckResult:
    check: Check
    command: CommandResult


@dataclass(frozen=True)
class AgentMetadata:
    adapter: str
    duration_seconds: float | None
    attempts: int | None
    max_attempts: int
    max_tool_calls: int
    max_tokens: int
    max_cost_usd: float


@dataclass(frozen=True)
class EvaluationResult:
    classification: Classification
    task: Task
    patch: Path
    checks: tuple[CheckResult, ...]
    reason: str | None = None
    run_id: str | None = None
    replay_of: str | None = None
    agent: AgentMetadata | None = None
