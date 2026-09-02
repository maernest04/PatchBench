# Task Format

## Purpose

A task contract defines the repository, execution limits, public checks, hidden checks, and optional private reviewer ground truth.

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
- `candidates/`: registered control and known-regression patches used to validate the evaluator. These are never exposed to an evaluated agent.

## Required task fields

```yaml
id: cache-invalidation-v1
version: 1
repository: repository

constraints:
  timeout_seconds: 30
  memory_megabytes: 256
  cpu_cores: 1

runtime:
  image: patchbench-python-pytest:0.1
  dockerfile: Dockerfile

reviewer_ground_truth: hidden/reviewer.yaml

candidates:
  - path: candidates/correct.patch
    kind: control
    provenance: human_authored
  - path: candidates/stale-cache.patch
    kind: known_regression
    provenance: observed_ai_style

checks:
  - type: pytest
    visibility: public
    path: public/tests
  - type: pytest
    visibility: hidden
    path: hidden/tests
  - type: differential
    visibility: hidden
    path: hidden/scenarios/delete_then_read.py
  - type: cli
    visibility: hidden
    command: [python, report.py, Grace Hopper, --output, /tmp/patchbench-output/report.json]
    expected:
      exit_code: 0
      stdout: "grace-hopper\n"
      files:
        report.json: "{\"name\": \"Grace Hopper\", \"slug\": \"grace-hopper\"}\n"
  - type: api
    visibility: hidden
    path: hidden/scenarios/lookup_compatibility.py
    expected:
      stdout: '[{"email":"missing@example.com","result":null}]'
```

`runtime.image` identifies the container image used for checks. When `runtime.dockerfile` is present, PatchBench builds that image from the task directory before executing checks. `reviewer_ground_truth` is optional and must point to a private YAML file inside the task directory.

```yaml
fault_id: stale-cache-after-delete
category: preservation
affected_paths:
  - user_store.py
affected_symbols:
  - UserStore.delete_user
```

## Contract rules

- A task has one versioned ID and one primary objective.
- Public files are the complete material available to an evaluated agent.
- Hidden files cannot be copied or mounted into the agent workspace.
- Checks define observable evidence, not an LLM-derived quality score.
- A differential check runs a scenario against baseline and candidate workspaces and compares their normalized output.
- A CLI check runs its command in the candidate workspace and verifies exact exit code, stdout, and files written beneath `/tmp/patchbench-output`.
- An API check runs a compatibility scenario in the candidate workspace and compares its normalized JSON observation with the declared contract output.
- A task must define enough conditions to classify a result honestly.
- An ambiguous task must return `INCONCLUSIVE` rather than create a misleading failure.
- Reviewer ground truth must stay under `hidden/` and must not be copied into a reviewer workspace.

## Candidate rules

Each task registers one `control` patch that passes public and hidden checks and one `known_regression` patch that passes public checks but fails a hidden contract. PatchBench only calculates reviewer recall and false-positive rates for registered candidates. The evaluator applies each unified diff only to a temporary candidate workspace.

Candidate provenance is `human_authored` or `observed_ai_style`.
