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
- [ ] Build and run the task's Docker execution environment with no network access by default.
- [ ] Enforce CPU, memory, process, and wall-clock limits.
- [ ] Run public checks and hidden checks independently.
- [x] Capture stdout, stderr, exit code, duration, and execution-failure reason.
- [x] Emit a human-readable report and a machine-readable JSON result.
- [x] Clean temporary workspaces after successful and failed runs.

### Exit criterion

`patchbench evaluate --task <task> --patch <patch>` classifies a supplied correct and incorrect fixture patch accurately.

## Phase 3: Evidence, preservation, and replay

### Goal

Turn a failed check into understandable, replayable evidence.

### Checklist

- [ ] Create structured models for commands, check results, findings, and evidence artifacts.
- [ ] Store task ID and version, patch digest, evaluator version, seed, and environment/image digest.
- [ ] Add a durable local run store.
- [ ] Add baseline execution when a task requires behavior preservation.
- [ ] Implement one deterministic differential evaluator.
- [ ] Preserve relevant operation sequences and normalized observations.
- [ ] Assign a run ID to each complete evaluation.
- [ ] Implement `patchbench show <run-id>`.
- [ ] Implement `patchbench replay <run-id>`.
- [ ] Verify a replay produces the original classification under the same environment.
- [ ] Ensure infrastructure failures become `INCONCLUSIVE`, not candidate `FAIL` results.

### Exit criterion

PatchBench detects a hidden behavioral regression that public tests miss and provides a replayable explanation of the failure.

## Phase 4: Evaluator quality and test rigor

### Goal

Demonstrate that PatchBench itself is trustworthy enough to evaluate candidate code.

### Checklist

- [ ] Unit-test schemas, task loading, patch validation, classification, normalization, and reporting.
- [ ] Integration-test Docker execution, public checks, hidden checks, and cleanup.
- [ ] Test malformed task definitions, invalid patches, command timeouts, and evaluator crashes.
- [ ] Test that hidden files are unavailable in the agent-visible workspace.
- [ ] Test that correct candidates pass and intentionally incorrect candidates fail.
- [ ] Repeat deterministic fixture runs to validate stability.
- [ ] Track false-positive and false-negative cases discovered during fixture design.
- [ ] Verify that evaluator failures are reported distinctly from candidate failures.

### Exit criterion

Every evaluator capability has a positive test, a negative test, and a defined failure classification.

## Phase 5: Expand task contracts

### Goal

Prove that PatchBench is a general software-task evaluator rather than a backend-only test runner.

### Checklist

- [ ] Add a CLI-output evaluator for commands, exit codes, and filesystem effects.
- [ ] Add a library/API-compatibility evaluator.
- [ ] Add a refactor task that relies on behavioral preservation.
- [ ] Add a task with an explicit policy or security constraint.
- [ ] Document extension points for frontend, mobile, performance, and infrastructure evaluators.
- [ ] Validate each new evaluator with correct and incorrect candidates.

### Exit criterion

At least three materially different task contracts use the same core task loader, workspace manager, evidence model, and reporter.

## Phase 6: Optional real-agent adapters

### Goal

Evaluate real coding agents only after the evaluator and benchmark fixtures are validated.

### Checklist

- [ ] Define a provider-neutral `AgentAdapter` contract.
- [ ] Define fixed agent budgets for time, attempts, tools, tokens, and cost.
- [ ] Add one adapter configured by environment variables.
- [ ] Keep credentials out of source control, logs, reports, and persisted evidence.
- [ ] Capture the final candidate patch and safe execution metadata.
- [ ] Evaluate fixture and agent-generated patches through exactly the same evaluator path.
- [ ] Report task result separately from time, cost, and number of attempts.

### Exit criterion

One real coding-agent attempt produces a candidate patch and a complete, reproducible PatchBench result without exposing credentials.

## Phase 7: Benchmark reporting

### Goal

Produce a transparent report that compares candidate sources without overstating conclusions.

### Checklist

- [ ] Run repeated attempts for each task and candidate source.
- [ ] Report task-success, hidden-failure, safety-violation, inconclusive, runtime, and reproducibility rates separately.
- [ ] Report task and evaluator limitations.
- [ ] Version benchmark tasks, evaluator behavior, and reports.
- [ ] Publish enough fixture metadata for independent reproduction without leaking hidden checks.

### Exit criterion

A versioned report compares at least two candidate sources across a small suite and documents its limits.

## Deferred work

- Web UI.
- Hosted or multi-tenant execution.
- Arbitrary-language support.
- Autonomous patch repair.
- Broad model rankings from insufficient task samples.
