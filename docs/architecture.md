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

## Planned change-contract generation extension

The implemented evaluator begins with a trusted task contract. The planned extension adds an upstream proposal flow for ordinary development changes; it does not replace the evaluator or give a model authority over results.

```text
Task request + candidate patch + repository summary
                         |
                         v
            Deterministic risk inventory
                         |
                         v
      Rule-based and optional LLM contract proposer
                         |
                         v
        Schema validation and explicit approval
                         |
                         v
      Existing isolated task-specific evaluator
                         |
                         v
          Evidence, result, and replay data
```

Only an approved, executable contract reaches the evaluator. A proposal is evidence for review, not evidence that the candidate is correct.

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

### Planned risk inventory and contract proposer

The risk inventory derives auditable signals from changed files, symbols, call sites, state transitions, public interfaces, and policy-relevant operations. The proposer maps those signals to structured contract proposals. It may use deterministic templates alone or an optional LLM that returns a bounded schema; neither path may access hidden evaluator material or classify a candidate as passing.

## Isolation requirements

- Network disabled by default.
- No host secrets.
- CPU, memory, process, and wall-clock limits.
- Temporary workspaces.
- Captured stdout, stderr, exit status, and relevant resource metadata.
