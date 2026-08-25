# Evaluation Specification

## Evaluation unit

One evaluation unit is one candidate change applied to one versioned task under a fixed environment, evaluator configuration, and seed.

## Task-specific evaluation contract

Every benchmark task defines the executable evidence needed to judge it. A task may specify acceptance checks, behavior-preservation checks, stateful sequences, policy constraints, performance thresholds, or a combination.

| Task type | Typical evidence |
|---|---|
| New feature | Hidden acceptance tests and invariants |
| Bug fix | Tests proving the defect is fixed, plus regression checks |
| Refactor | Behavioral equivalence and public API compatibility |
| Frontend task | End-to-end interaction, accessibility, or visual assertions |
| CLI task | Inputs, outputs, exit codes, and filesystem effects |
| Infrastructure task | Plan validation, sandboxed simulation, and policy checks |
| Security task | Explicit security invariants and adversarial tests |
| Performance task | Correctness checks plus benchmark thresholds |

## Dimensions

### Task correctness

The candidate satisfies the requested new or changed behavior.

### Behavior preservation

The candidate preserves behavior the task does not authorize changing.

### Stateful correctness

The candidate behaves correctly across bounded operation sequences, retries, lifecycle transitions, or concurrent operations when relevant.

### Safety

The candidate respects explicit constraints, such as authorization boundaries, data handling, secret safety, or no-destructive-action policies.

### Reliability

The candidate produces stable results across repeated deterministic runs. Managed nondeterminism must be recorded.

### Efficiency

PatchBench records elapsed time, attempts, and resource use. Efficiency never compensates for a failing correctness or safety result.

## Result classification

- `PASS`: all required checks pass and no relevant failure is found by enabled evaluators.
- `FAIL`: a required check fails or a reproducible relevant failure is found.
- `INCONCLUSIVE`: the environment fails, the contract is insufficient, or the evaluator cannot reach a trustworthy result.

## Failure evidence

Every `FAIL` must retain the task ID, candidate revision, failed check, expected and observed behavior, relevant inputs or operation sequence, environment metadata, seed, and replay instructions.

## Aggregate reporting

Report task-success rate, hidden-failure rate, safety-violation rate, inconclusive rate, median and p95 runtime, and reproducibility rate separately.

