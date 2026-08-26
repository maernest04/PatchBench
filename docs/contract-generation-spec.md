# Change-Contract Generation Specification

## Purpose

PatchBench's existing evaluator answers whether a candidate satisfies a trusted executable contract. Change-contract generation addresses the earlier question: given an AI-authored change, what new evidence should a reviewer require before trusting it?

It produces reviewable hypotheses for regression, preservation, compatibility, and policy contracts. It does not claim to prove a change correct from static analysis or model judgment.

## Inputs and boundaries

The generation context contains only material that is safe for the proposer to inspect:

- The task request or developer intent.
- The candidate patch and affected repository files.
- A bounded repository summary, such as public interfaces, direct call sites, configured commands, and existing public checks.
- Deterministic risk findings.

Hidden tests, hidden expected outcomes, reference patches, credentials, and prior hidden-check results are excluded from the context. A proposal is retained by PatchBench for review and is not supplied back to the evaluated coding agent.

## Proposal schema

Each proposal will use a versioned structured record with these fields:

| Field | Meaning |
|---|---|
| `id` | Stable proposal identifier. |
| `kind` | Allowed contract type: `pytest`, `differential`, `cli`, `api`, or `policy`. |
| `category` | Correctness, preservation, safety, reliability, or efficiency. |
| `risk_ids` | The deterministic findings that motivated the proposal. |
| `title` | Short description of the behavior to establish. |
| `rationale` | Why the changed code could violate this behavior. |
| `evidence` | Changed paths, symbols, call sites, or operations supporting the rationale. |
| `scenario` | Declarative inputs or operation sequence to execute. |
| `assertion` | Observable outcome the approved contract must check. |
| `confidence` | Triage level for review priority, never a probability or result. |
| `status` | `proposed`, `approved`, or `rejected`. |

The initial schema accepts only contract types the existing evaluator can isolate and replay. Unsupported or incomplete proposals are rejected with a retained reason.

## Lifecycle

1. PatchBench creates a deterministic risk inventory from the generation context.
2. A template proposer maps supported findings to contract hypotheses. An optional LLM may add schema-conforming proposals from the same bounded context.
3. PatchBench validates every proposal for schema conformance, supported execution, evidence linkage, and hidden-material boundaries.
4. A developer or trusted rule explicitly approves or rejects each valid proposal.
5. PatchBench materializes an approved proposal as a trusted task-contract change.
6. The existing isolated evaluator executes it and stores evidence, result, and replay data.

## Authority model

Only executed checks determine `PASS`, `FAIL`, or `INCONCLUSIVE`. A proposal may prioritize reviewer attention but cannot block, approve, or score a candidate on its own.

If a proposal is unavailable, rejected, or insufficiently executable, PatchBench reports that coverage gap. If the trusted contract cannot support a conclusion, the evaluator reports `INCONCLUSIVE`.

## Optional LLM proposer

An LLM provider is optional. When configured, it must return the proposal schema only and must receive bounded, redacted context. PatchBench records provider/model metadata and context digests, not credentials, raw secrets, or hidden materials.

The LLM is useful for connecting a request's intent to a non-obvious behavior scenario. Deterministic validation, explicit approval, and sandboxed execution constrain that suggestion before it can affect evidence.

## Success measures

- Proposal acceptance rate by risk category.
- Percentage of accepted proposals that execute successfully.
- Regressions caught by approved generated contracts after visible checks passed.
- Unsupported, rejected, and inconclusive proposal rate.
- Replay agreement for evaluations that use approved generated contracts.
