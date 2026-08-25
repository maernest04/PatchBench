# Architecture

## Overview

PatchBench separates the generic evaluation engine from task-specific evaluators and optional coding-agent adapters.

```text
Benchmark task + agent configuration
                |
                v
       Agent adapter or fixture patch
                |
                v
         Candidate workspace manager
                |
                v
      Isolated task-specific evaluator
                |
                v
       Evidence store and report generator
```

## Components

### Benchmark registry

Loads versioned tasks and preserves the boundary between public agent materials and hidden evaluator materials.

### Agent adapter

Optionally runs a coding agent under a fixed task, budget, and workspace. The core evaluator does not require an adapter; fixture patches are valid candidates.

Future adapters may use provider credentials supplied through environment variables. Credentials must never be committed, logged, or stored in results.

### Workspace manager

Creates isolated candidate workspaces without modifying the benchmark source.

### Evaluator

Runs the task’s public and hidden checks, including acceptance, preservation, stateful, policy, and performance checks where applicable. It distinguishes evaluation-infrastructure failures from candidate failures.

### Evidence store

Persists task metadata, candidate revision, checks, logs, seeds, observations, classifications, and replay data.

### Reporter

Creates human-readable and machine-readable results while preserving separate dimensions instead of an opaque score.

## Isolation requirements

- Network disabled by default.
- No host secrets.
- CPU, memory, process, and wall-clock limits.
- Temporary workspaces.
- Captured stdout, stderr, exit status, and relevant resource metadata.

