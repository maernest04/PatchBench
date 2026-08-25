# PatchBench Development Guide

## Purpose

PatchBench evaluates AI coding agents through executed, task-specific evidence. Every feature must improve evaluation validity, reproducibility, safety, usability, or benchmark quality.

## Scope discipline

- Keep the core evaluator independent of any model provider.
- Support a task type only when it has a clear executable evaluation contract.
- Start with Python, pytest, local isolation, and curated fixtures.
- Defer web interfaces, hosted execution, arbitrary-language support, autonomous repair, and broad model rankings.
- Treat real-agent adapters as optional later integrations; the evaluator must work with fixture patches alone.

## Engineering principles

- Evidence beats an unsupported score.
- A baseline is evidence of current behavior, not proof of correctness.
- Separate task success from preservation of behavior that must not change.
- Preserve public and hidden evaluation materials as separate boundaries.
- Keep fixture repositories small and focused on one primary behavior.
- Prefer small, explicit code paths over speculative abstractions.

## Change discipline

- Make the smallest change that satisfies the request.
- Do not refactor unrelated code or reformat files unnecessarily.
- Do not add dependencies without a concrete, documented need.
- Keep documentation accurate; label unimplemented behavior as planned.

## Verification expectations

- Run relevant tests after code changes.
- Validate each evaluator with both correct and intentionally incorrect candidates.
- Record execution metadata and deterministic seeds whenever generated inputs are used.
- Do not classify evaluator or infrastructure failures as agent failures.

## Evaluation integrity

- Never expose hidden tests, reference patches, or hidden expected outcomes to evaluated agents.
- Do not use an LLM judge as final authority for executable behavior.
- Report `INCONCLUSIVE` when the evaluator or task contract cannot support a trustworthy conclusion.
- Report limitations, false positives, and inconclusive results with positive findings.

