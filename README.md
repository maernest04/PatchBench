# PatchBench

PatchBench measures whether AI reviewers can detect AI-authored code regressions that pass visible tests.

Rather than treating an LLM review as proof, PatchBench gives a reviewer agent a repository, public task materials, and a plausible candidate patch. It deterministically scores the review against private ground truth established by hidden executable checks.

## Core question

> Can an AI reviewer identify a behavioral regression that visible tests missed?

## Scope

PatchBench supports any software task with a clear, executable evaluator: backend services, frontends, CLIs, libraries, mobile apps, data pipelines, infrastructure, security fixes, performance work, refactors, and bug fixes.

The first implementation will use a small set of Python and pytest fixtures so the evaluator can become reliable before its supported task types expand.

## How it works

```text
Candidate patch + repository + public materials
                    |
                    v
             AI reviewer
                    |
                    v
          Structured finding
                    |
                    v
Private ground truth + deterministic scorer
                    |
                    v
   Stored evidence and benchmark report
```

## Benchmark direction

The evaluator establishes each candidate's ground truth. The pilot corpus contains six plausible, visible-test-passing regressions and the reviewer harness supports structured findings from a public-only workspace. `patchbench review-report` aggregates stored reviewer outcomes; controlled repeated experiments and executable reviewer artifacts remain future work.

## Repository guide

- [Benchmark specification](docs/benchmark-spec.md)
- [Architecture](docs/architecture.md)
- [Task format](docs/task-format.md)
- [CLI specification](docs/cli-spec.md)
- [Build plan](docs/implementation-plan.md)
