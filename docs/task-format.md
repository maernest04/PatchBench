# Task Format

## Purpose

A task contract describes what an evaluated agent may see, what PatchBench must evaluate privately, and how the result is determined.

## Directory shape

```text
fixtures/<task-id>/
├── task.yaml
├── repository/
├── public/
├── hidden/
└── candidates/
```

- `repository/`: initial codebase.
- `public/`: task description and any tests the agent may inspect.
- `hidden/`: acceptance, preservation, policy, or scenario checks visible only to PatchBench.
- `candidates/`: known-good and known-bad patches used to validate the evaluator. These are never exposed to an evaluated agent.

## Required task fields

```yaml
id: cache-invalidation-v1
version: 1
language: python
repository: repository

public:
  task: public/task.md
  tests: public/tests

hidden:
  tests: hidden/tests

constraints:
  network: disabled
  timeout_seconds: 30
  memory_megabytes: 512

checks:
  - type: pytest
    visibility: public
    path: public/tests
  - type: pytest
    visibility: hidden
    path: hidden/tests
```

The exact schema is finalized in Phase 0. This example communicates the boundary and does not yet define every supported field.

## Contract rules

- A task has one versioned ID and one primary objective.
- Public files are the complete material available to an evaluated agent.
- Hidden files cannot be copied or mounted into the agent workspace.
- Checks define observable evidence, not an LLM-derived quality score.
- A task must define enough conditions to classify a result honestly.
- An ambiguous task must return `INCONCLUSIVE` rather than create a misleading failure.

## Candidate rules

V1 accepts a unified diff. The evaluator applies it only to a temporary candidate workspace. A future agent adapter may generate the same diff, but it uses the identical evaluation path.

