# Product Specification

## Problem

AI coding agents can produce changes that compile and pass visible tests while failing the requested behavior, violating a constraint, or breaking behavior that is only visible after a sequence of operations.

## Product statement

PatchBench is an execution-based verification system that evaluates whether AI-authored changes complete software-engineering tasks according to task-specific, executable contracts. Its planned change-contract generator will turn a request, patch, and repository context into reviewable proposals for the evidence a change should satisfy.

## Users

- Engineers validating an agent-produced change.
- Researchers comparing coding agents.
- Platform teams establishing repeatable quality gates for coding agents.

## Inputs

- A versioned benchmark task.
- A repository and initial state.
- Public task materials and tests available to the agent.
- A candidate change created by an agent or fixture.
- Hidden evaluators and constraints available only to PatchBench.
- For contract generation, a repository summary and deterministic risk inventory derived from the requested change and candidate patch.

## Outputs

- `PASS`, `FAIL`, or `INCONCLUSIVE`.
- Evidence for each result.
- Task-success, preservation, safety, reliability, and efficiency observations.
- Reproduction metadata for relevant failures.
- When enabled, reviewable proposed contracts with their evidence, risk category, and approval status.

## Non-goals for the first release

- Proving arbitrary code universally correct or secure.
- Replacing human review for ambiguous requirements.
- Reducing an agent to one opaque quality score.
- Requiring an LLM provider or API key for the core evaluator.
- Allowing an LLM to declare a change correct without executed evidence.
- Automatically installing or executing an unreviewed generated contract in the first contract-generation release.
