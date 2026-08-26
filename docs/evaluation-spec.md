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

## Proposed contracts

Change-contract generation may propose new checks from the task request, candidate patch, repository context, and deterministic risk inventory. A proposal is not an evaluator and cannot produce `PASS` or `FAIL`.

Before a proposal can affect a result, PatchBench must validate its schema, retain its rationale and source evidence, and require explicit developer or trusted-rule approval. The resulting executable contract then runs through the same isolated evaluator and evidence path as every other task contract.

An optional LLM can produce structured proposals, but it must not receive hidden tests, hidden expected outcomes, or prior hidden-check results. It is never the final authority for executable behavior. If the available contract cannot support a trustworthy conclusion, PatchBench reports `INCONCLUSIVE` rather than relying on a proposal's confidence.

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
