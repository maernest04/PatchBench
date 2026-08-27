# Benchmark Specification

## Question

Can an AI reviewer detect and expose a behavioral regression in a plausible candidate patch when the task's visible tests pass?

## Task design

Each versioned task contains a small reproducible repository, public task request and tests, a plausible incorrect candidate patch, a correct reference or verified baseline, and a hidden executable contract.

The incorrect candidate must pass all public checks and fail the hidden contract. The correct reference or baseline must pass the hidden contract. Each task has one primary regression, private ground-truth fault labels, candidate provenance, and no dependency on secrets, external network access, or unmanaged services.

The first corpus will contain 15–25 Python tasks across state/lifecycle behavior, public API compatibility, CLI/filesystem behavior, security/policy, refactor preservation, and reliability/error paths. The pilot now contains one task from each category.

## Reviewer inputs and outputs

A reviewer receives only the repository, task request, public tests, candidate patch, fixed prompt, and declared tool/budget policy. It never receives hidden checks, expected outcomes, reference patches, private fault labels, or prior results.

The reviewer returns a structured finding: claimed category, affected path or symbol, rationale, confidence, and an optional executable verification artifact. A reviewer may explicitly state that it cannot reach a conclusion.

## Scoring

PatchBench establishes candidate ground truth with the hidden contract before scoring any review.

- `detected`: the finding matches the task-authored affected behavior evidence. Category is supporting evidence and may differ when the same regression has a valid alternate framing.
- `executable_detected`: a detection plus an artifact that fails on the incorrect candidate and passes on the correct reference or baseline.
- `missed`: no finding identifies the known regression.
- `false_positive`: the reviewer asserts a defect without task-ground-truth or executable support.
- `inconclusive`: the reviewer, scorer, or execution environment cannot support a trustworthy result.

The scorer uses pre-authored labels and executed artifacts, never an LLM judge. A review score never changes the candidate's ground truth.

## Ground-truth evaluation

PatchBench classifies candidate execution as `PASS`, `FAIL`, or `INCONCLUSIVE`.

- `PASS`: every required check passes.
- `FAIL`: a required check fails with retained execution evidence.
- `INCONCLUSIVE`: the environment, task contract, or evaluator cannot support a trustworthy conclusion.

Tasks may combine acceptance, preservation, stateful, safety, reliability, and efficiency checks. Every hidden-regression task must prove that its incorrect candidate passes public checks, fails hidden checks, and can be replayed. Correct references must pass the same hidden checks.

## Comparison protocol

Each frozen corpus is evaluated with three workflows:

| Workflow | Purpose |
|---|---|
| Public-test baseline | Proves the candidate appears valid to visible checks. |
| Text-only review | Measures whether a reviewer can identify the defect from public materials and the patch. |
| Executable-evidence review | Measures whether a reviewer can provide a check that exposes the defect. |

For a run, freeze corpus version, task list, prompt, model configuration, enabled tools, time/token/cost/retry budgets, attempt count, evaluator version, scorer version, and report version. Run at least three independent attempts per task and workflow where budget permits. Do not combine different configurations without labeling them as separate experiments.

## Reporting

Report detection, executable-detection, miss, false-positive, inconclusive, runtime, cost when available, and replay agreement overall and by category. Preserve raw per-task outcomes and show every aggregate's numerator and denominator.

Each report records the corpus, prompt, reviewer configuration, tool policy, budgets, environment, evaluator, scorer, and known threats to validity. Results apply only to the named corpus and configuration; PatchBench does not claim a broad model ranking from a small curated set.

## Release and leakage

Task versions and evaluators are immutable once released. Public materials, candidate patches, category metadata, and evaluator versions may be published. Active hidden checks, reference patches, exact accepted labels, and expected outcomes stay sealed until a benchmark version is retired or separately disclosed.

## Benchmark quality

Unit tests cover task parsing, patch validation, scoring, classification, normalization, and reporting. Integration tests cover temporary workspaces, Docker execution, public and hidden checks, persistence, and cleanup. Every fixture needs a correct candidate, a visible-test-passing incorrect candidate, and defined infrastructure-failure behavior. Record suspected false positives and false negatives with their task version and evidence.
