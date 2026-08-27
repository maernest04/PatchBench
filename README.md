# PatchBench

PatchBench is a benchmark for measuring whether AI reviewers can detect AI-authored code regressions that pass visible tests.

Rather than treating an LLM review as proof, PatchBench gives a reviewer agent a task, repository, public checks, and a plausible candidate patch. It then measures whether the reviewer identifies and exposes the patch's hidden behavioral regression through reproducible execution.

## Core question

> Can an AI reviewer identify a behavioral regression that visible tests missed, and produce evidence that exposes it?

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

## Benchmark direction

The existing evaluator is the benchmark's execution engine. The next phase builds a curated corpus of plausible, visible-test-passing regressions and a controlled reviewer-agent experiment harness. PatchBench will compare visible tests, a text-only AI review, and an AI reviewer that produces executable verification evidence. It reports what reviewers catch, miss, and cannot evaluate—not an unsupported overall model ranking.

## Repository guide

- [Benchmark specification](docs/benchmark-spec.md)
- [Architecture](docs/architecture.md)
- [Task format](docs/task-format.md)
- [CLI specification](docs/cli-spec.md)
- [Build plan](docs/implementation-plan.md)
