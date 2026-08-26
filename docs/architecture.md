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

## Planned reviewer benchmark extension

The implemented evaluator establishes whether a candidate patch is actually incorrect. The planned extension measures whether a reviewer agent can discover that issue without access to hidden materials.

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

### Planned reviewer scorer

The scorer matches a reviewer finding against task-authored ground-truth labels and validates any reviewer-produced verification artifact by execution. Text alone can establish a declared detection; only a distinguishing executable artifact establishes executable detection. Neither score changes the candidate's hidden ground truth.

## Isolation requirements

- Network disabled by default.
- No host secrets.
- CPU, memory, process, and wall-clock limits.
- Temporary workspaces.
- Captured stdout, stderr, exit status, and relevant resource metadata.
