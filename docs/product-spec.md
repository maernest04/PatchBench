# Product Specification

## Problem

AI coding agents can produce changes that compile and pass visible tests while failing the requested behavior, violating a constraint, or breaking behavior that is only visible after a sequence of operations.

## Product statement

PatchBench is an execution-based benchmark framework that evaluates whether AI coding agents complete software-engineering tasks according to task-specific, executable contracts.

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

## Outputs

- `PASS`, `FAIL`, or `INCONCLUSIVE`.
- Evidence for each result.
- Task-success, preservation, safety, reliability, and efficiency observations.
- Reproduction metadata for relevant failures.

## Non-goals for the first release

- Proving arbitrary code universally correct or secure.
- Replacing human review for ambiguous requirements.
- Reducing an agent to one opaque quality score.
- Requiring an LLM provider or API key for the core evaluator.

