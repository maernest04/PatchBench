# Architecture

## Overview

PatchBench separates its generic execution engine from benchmark tasks and optional reviewer-agent adapters.

```text
Benchmark task + reviewer configuration
                |
                v
  Candidate patch + public task materials
                |
                v
       Reviewer adapter and structured finding
                |
                v
  Isolated ground-truth and reviewer-check evaluation
                |
                v
       Evidence store and report generator
```

## Reviewer benchmark workflow

The evaluator establishes whether a candidate patch is actually incorrect. The reviewer workflow measures whether a configured reviewer command can identify that issue without access to hidden materials. Executable reviewer artifacts remain a later extension.

```text
Public task + repository + candidate patch
                    |
                    v
       Fixed-budget reviewer-agent attempt
                    |
                    v
Structured finding and optional verification artifact
                    |
                    v
  Deterministic scorer + hidden ground-truth evaluator
                    |
                    v
   Per-task outcome, evidence, and aggregate report
```

The hidden evaluator decides candidate ground truth. The scorer decides whether the reviewer's evidence actually identified or exposed that known regression. The reviewer never receives hidden tests, reference patches, or prior hidden results.

## Components

### Benchmark registry

Loads versioned tasks and preserves the boundary between public agent materials and hidden evaluator materials.

### Reviewer adapter

Optionally runs a reviewer agent under a fixed prompt, budget, and public workspace. The adapter returns structured findings and, where permitted, a verification artifact. Fixture findings remain valid baseline inputs for scorer tests.

Future adapters may use provider credentials supplied through environment variables. Credentials must never be committed, logged, or stored in results.

### Workspace manager

Creates isolated candidate workspaces without modifying the benchmark source.

### Evaluator

Runs the task’s public and hidden checks, including acceptance, preservation, stateful, policy, and performance checks where applicable. It distinguishes evaluation-infrastructure failures from candidate failures.

### Evidence store

Persists task metadata, candidate revision, checks, logs, seeds, observations, classifications, and replay data.

### Reporter

Creates human-readable and machine-readable results while preserving separate dimensions instead of an opaque score.

### Reviewer scorer

The scorer matches a reviewer finding against task-authored ground-truth labels. It records detected, missed, false-positive, or inconclusive outcomes without changing candidate ground truth. A later extension will validate reviewer-produced verification artifacts by execution.

## Repository layout

```text
src/patchbench/
├── cli.py
├── models.py
├── task_loader.py
├── workspace.py
├── runner.py
├── evaluator.py
├── review_scoring.py
├── replay.py
├── reporter.py
├── agents.py
└── storage/
```

- `models.py` defines task, evaluation, and reviewer-finding records.
- `task_loader.py` loads public and hidden task metadata without exposing hidden files to agents.
- `workspace.py`, `runner.py`, and `evaluator.py` create isolated candidate workspaces and establish ground truth.
- `review_scoring.py` compares a reviewer finding with private task labels.
- `agents.py` contains the current candidate-generating adapter; a reviewer adapter will be a separate public-only integration.
- `storage/`, `replay.py`, and `reporter.py` persist and present reproducible evidence.

New evaluator types must use the existing task loader, workspace manager, Docker runner, evidence model, reporter, and run store. They define observable execution, public and hidden boundaries, deterministic pass/fail conditions, and when an environment error becomes `INCONCLUSIVE`.

## Isolation requirements

- Network disabled by default.
- No host secrets.
- CPU, memory, process, and wall-clock limits.
- Temporary workspaces.
- Captured stdout, stderr, exit status, and relevant resource metadata.
