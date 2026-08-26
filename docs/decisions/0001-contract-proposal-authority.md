# Decision 0001: Contract proposals are not evaluation authority

## Context

PatchBench needs to help developers discover the behavior an AI-authored patch should prove, not merely execute checks that were written in advance. An LLM can help formulate useful scenarios from a task request and repository context, but a model judgment is not reliable evidence that code works.

## Decision

PatchBench will treat deterministic rules and optional LLM output as contract proposers only. Every proposal must be schema-validated, linked to explicit risk evidence, and explicitly approved before it becomes an executable task contract. The existing isolated evaluator is the only component that may classify a candidate as `PASS`, `FAIL`, or `INCONCLUSIVE`.

Proposers must not receive hidden tests, hidden expected outcomes, reference patches, credentials, or prior hidden-check results. Proposal confidence is triage metadata, not a correctness score.

## Consequences

The product can use LLM reasoning without making its central claim depend on an LLM judge. The first implementation requires a review step, which adds friction but prevents silently running unsafe or invalid generated checks. It also preserves the hidden-material boundary and ensures generated contracts use the same reproducible Docker, evidence, and replay path as manually authored ones.
