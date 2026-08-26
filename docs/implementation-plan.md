# Implementation Plan

## V1 boundary

V1 evaluates a supplied unified diff against a versioned Python/pytest task. It does not require an LLM, call an external model provider, or run an autonomous agent. Its job is to prove that the evaluation engine produces valid, reproducible evidence before real-agent integration begins.

V1 uses Docker-based isolation for candidate execution. The project must not claim that host-subprocess execution is a secure boundary for untrusted generated code.

## Phase 0: Contracts and fixture design

### Goal

Define precisely what PatchBench evaluates and what evidence is required for every result.

### Checklist

- [x] Create `task.schema.json`, `run.schema.json`, and `result.schema.json`.
- [x] Define `PASS`, `FAIL`, and `INCONCLUSIVE` result rules.
- [x] Define a task contract containing public materials, hidden checks, constraints, and evaluator configuration.
- [x] Define stable CLI exit codes.
- [ ] Define the run-evidence record, including task version, patch digest, command observations, environment metadata, and seed.
- [x] Document the public-versus-hidden material boundary.
- [ ] Record why V1 uses Python, pytest, and Docker in decision records.
- [x] Define how a candidate patch is supplied and validated.

### Exit criterion

A reviewer can inspect a task definition and determine exactly what produces `PASS`, `FAIL`, or `INCONCLUSIVE` without reading implementation code.

## Phase 1: Fixture-first evaluator validation

### Goal

Prove that the benchmark design catches meaningful failures that visible tests alone do not detect.

### Checklist

- [x] Create a cache-invalidation fixture with a stateful hidden regression.
- [ ] Create a CLI or library-behavior fixture.
- [x] Give every fixture a public task description and public tests.
- [x] Give every fixture hidden acceptance or preservation checks.
- [x] Create one independently verified correct candidate patch per fixture.
- [x] Create one realistic incorrect candidate patch per fixture.
- [x] Ensure at least one incorrect candidate passes the visible tests but fails hidden checks.
- [x] Ensure fixtures require no secrets, network access, or unmanaged external services.
- [ ] Document each fixture's expected outcomes without exposing hidden details to an evaluated agent.

### Exit criterion

Each fixture demonstrates a specific gap between visible-test success and task correctness.

## Phase 2: Minimal local evaluator

### Goal

Evaluate one candidate patch against one task with a single CLI command.

### Checklist

- [x] Scaffold the `patchbench` Python package and CLI entry point.
- [x] Load and validate `task.yaml` against the task schema.
- [x] Create a temporary baseline workspace and candidate workspace.
- [x] Validate and apply a unified diff only inside the candidate workspace.
- [x] Build and run the task's Docker execution environment with no network access by default.
- [x] Enforce CPU, memory, process, and wall-clock limits.
- [x] Run public checks and hidden checks independently.
- [x] Capture stdout, stderr, exit code, duration, and execution-failure reason.
- [x] Emit a human-readable report and a machine-readable JSON result.
- [x] Clean temporary workspaces after successful and failed runs.

### Exit criterion

`patchbench evaluate --task <task> --patch <patch>` classifies a supplied correct and incorrect fixture patch accurately.

## Phase 3: Evidence, preservation, and replay

### Goal

Turn a failed check into understandable, replayable evidence.

### Checklist

- [x] Create structured models for commands, check results, and evidence artifacts.
- [ ] Store task ID and version, patch digest, evaluator version, seed, and environment/image digest.
- [x] Add a durable local run store.
- [x] Add baseline execution when a task requires behavior preservation.
- [x] Implement one deterministic differential evaluator.
- [x] Preserve relevant operation sequences and normalized observations.
- [x] Assign a run ID to each complete evaluation.
- [x] Implement `patchbench show <run-id>`.
- [x] Implement `patchbench replay <run-id>`.
- [x] Verify a replay produces the original classification under the same environment.
- [x] Ensure infrastructure failures become `INCONCLUSIVE`, not candidate `FAIL` results.

### Exit criterion

PatchBench detects a hidden behavioral regression that public tests miss and provides a replayable explanation of the failure.

## Phase 4: Evaluator quality and test rigor

### Goal

Demonstrate that PatchBench itself is trustworthy enough to evaluate candidate code.

### Checklist

- [x] Unit-test schemas, task loading, patch validation, classification, normalization, and reporting.
- [x] Integration-test Docker execution, public checks, hidden checks, and cleanup.
- [x] Test malformed task definitions, invalid patches, command timeouts, and evaluator crashes.
- [x] Test that hidden files are unavailable in the agent-visible workspace.
- [x] Test that correct candidates pass and intentionally incorrect candidates fail.
- [x] Repeat deterministic fixture runs to validate stability.
- [x] Track false-positive and false-negative cases discovered during fixture design.
- [x] Verify that evaluator failures are reported distinctly from candidate failures.

### Exit criterion

Every evaluator capability has a positive test, a negative test, and a defined failure classification.

## Phase 5: Expand task contracts

### Goal

Prove that PatchBench is a general software-task evaluator rather than a backend-only test runner.

### Checklist

- [x] Add a CLI-output evaluator for commands, exit codes, and filesystem effects.
- [x] Add a library/API-compatibility evaluator.
- [x] Add a refactor task that relies on behavioral preservation.
- [x] Add a task with an explicit policy or security constraint.
- [x] Document extension points for frontend, mobile, performance, and infrastructure evaluators.
- [x] Validate each new evaluator with correct and incorrect candidates.

### Exit criterion

At least three materially different task contracts use the same core task loader, workspace manager, evidence model, and reporter.

## Phase 6: Optional real-agent adapters

### Goal

Evaluate real coding agents only after the evaluator and benchmark fixtures are validated.

### Checklist

- [x] Define a provider-neutral `AgentAdapter` contract.
- [x] Define fixed agent budgets for time, attempts, tools, tokens, and cost.
- [x] Add one adapter configured by environment variables.
- [x] Keep credentials out of source control, logs, reports, and persisted evidence.
- [x] Capture the final candidate patch and safe execution metadata.
- [x] Evaluate fixture and agent-generated patches through exactly the same evaluator path.
- [x] Report task result separately from time, cost, and number of attempts.

### Exit criterion

One real coding-agent attempt produces a candidate patch and a complete, reproducible PatchBench result without exposing credentials.

## Phase 7: Benchmark reporting

### Goal

Produce a transparent report that compares candidate sources without overstating conclusions.

### Checklist

- [x] Run repeated attempts for each task and candidate source.
- [x] Report task-success, hidden-failure, safety-violation, inconclusive, runtime, and reproducibility rates separately.
- [x] Report task and evaluator limitations.
- [x] Version benchmark tasks, evaluator behavior, and reports.
- [ ] Publish enough fixture metadata for independent reproduction without leaking hidden checks.

### Exit criterion

A versioned report compares at least two candidate sources across a small suite and documents its limits.

## Phase 8: Reviewer-regression corpus

### Goal

Create a curated corpus of plausible incorrect patches that pass visible tests but fail one clear hidden behavioral contract. The corpus is the benchmark's central artifact; the existing evaluator establishes each task's ground truth.

### Phase 8A: Corpus contract and pilot

- [ ] Define the versioned reviewer-task schema, ground-truth fault labels, candidate provenance, and public-versus-hidden layout.
- [ ] Define task authoring rules: one primary hidden regression, one correct reference, one plausible incorrect candidate, and public-test-pass proof.
- [ ] Build a six-task pilot spanning state/lifecycle, API compatibility, CLI/filesystem behavior, redaction/authorization, refactor preservation, and reliability/error paths.
- [ ] Record per-task author rationale, candidate plausibility review, deterministic environment, and hidden-evaluator evidence without leaking the fault to reviewer agents.
- [ ] Validate each pilot task against its incorrect candidate, correct reference, and at least one irrelevant reviewer finding.

### Phase 8B: Corpus expansion and quality

- [ ] Expand to 15–25 tasks with at least three tasks per major category.
- [ ] Include both human-authored and observed AI-style failure patterns; label provenance accurately.
- [ ] Add task-level difficulty and confound review to avoid trivial test-name, diff-size, or naming leaks.
- [ ] Add a correct-reference and incorrect-candidate replay check to the corpus release process.
- [ ] Version and freeze the first corpus release before running comparison experiments.

### Exit criterion

At least six pilot tasks each prove that the incorrect candidate passes public checks, fails a hidden contract, and can be replayed; no public material reveals the task's fault label.

## Phase 9: Reviewer-agent evaluation harness

### Goal

Measure whether an AI reviewer identifies the corpus's known regression without receiving hidden information.

### Checklist

- [ ] Define a structured reviewer-finding schema containing claimed category, affected paths or symbols, rationale, confidence, and optional verification artifact.
- [ ] Define a provider-neutral reviewer adapter with fixed time, tool, token, cost, and retry budgets.
- [ ] Build a public-only reviewer workspace containing the repository, task, public tests, and incorrect candidate patch.
- [ ] Implement deterministic scoring against pre-authored ground-truth fault labels.
- [ ] Validate executable artifacts by running them against the incorrect candidate and correct reference or baseline as appropriate.
- [ ] Classify detection, executable detection, miss, false positive, and inconclusive independently.
- [ ] Preserve prompt version, safe adapter metadata, artifacts, scorer output, and replay data.

### Planned module layout

```text
src/patchbench/
├── reviewer_models.py
├── reviewers.py
├── review_scoring.py
└── review_reporting.py
```

### Exit criterion

One reviewer adapter completes the six-task pilot without hidden-material access, and scorer tests cover correct detection, wrong detection, executable detection, false positive, and infrastructure inconclusive outcomes.

## Phase 10: Controlled comparison and report

### Goal

Produce transparent evidence of what reviewer workflows add beyond public tests and text-only review.

### Checklist

- [ ] Freeze a fixed reviewer prompt, model configuration, tools, budgets, and attempt count before each experiment.
- [ ] Run a public-test baseline, text-only reviewer baseline, and executable-evidence reviewer workflow over the frozen corpus.
- [ ] Run at least three independent attempts per task and workflow where cost permits.
- [ ] Report detection, executable-detection, false-positive, inconclusive, runtime, cost, and replay metrics by category and task.
- [ ] Publish per-task evidence and explicit threats to validity without publishing active hidden checks.
- [ ] State that results apply only to the named corpus, reviewer configurations, and experiment date.

### Exit criterion

A versioned report compares the three workflows on the frozen corpus, includes raw per-task outcomes and replay evidence, and makes no unsupported general ranking claim.

## Deferred work

- Web UI.
- Hosted or multi-tenant execution.
- Arbitrary-language support.
- Automated change-contract generation.
- Autonomous patch repair.
- Broad model rankings from insufficient task samples.
