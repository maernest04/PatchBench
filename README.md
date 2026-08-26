# PatchBench

PatchBench is an execution-based verification system for AI-authored code changes.

It measures whether an agent completes a software-engineering task according to an executable contract. Rather than trusting a visible test suite or asking an LLM to judge a patch, PatchBench runs the resulting code in a controlled environment and stores reproducible evidence.

## Core question

> Did the change complete the task correctly, preserve required behavior, and respect explicit constraints—and what executable contract would prove it?

## Scope

PatchBench supports any software task with a clear, executable evaluator: backend services, frontends, CLIs, libraries, mobile apps, data pipelines, infrastructure, security fixes, performance work, refactors, and bug fixes.

The first implementation will use a small set of Python and pytest fixtures so the evaluator can become reliable before its supported task types expand.

## How it works

```text
Task + repository + public materials
                |
                v
          AI coding agent
                |
                v
          Candidate code change
                |
                v
  Isolated, task-specific evaluator
                |
                v
 Evidence, result, and replay data
```

## Planned direction: change-contract generation

The existing evaluator executes trusted, task-specific contracts. The next product phase will make it useful during normal AI-assisted development: PatchBench will inspect a request, patch, and repository context; inventory the change's risks; and propose concrete regression, preservation, compatibility, or policy contracts for review. A developer or trusted rule set must approve a proposal before execution. An LLM may help propose a contract, but it never decides whether a change passes.

## Repository guide

- [Product specification](docs/product-spec.md)
- [Evaluation specification](docs/evaluation-spec.md)
- [Benchmark specification](docs/benchmark-spec.md)
- [Architecture](docs/architecture.md)
- [Contract-generation specification](docs/contract-generation-spec.md)
- [Risk model](docs/risk-model.md)
- [Implementation plan](docs/implementation-plan.md)
- [Development notes](docs/development-notes.md)
- [Agent adapters](docs/agent-adapters.md)
- [Benchmark reporting](docs/benchmark-reporting.md)

# PatchBench
