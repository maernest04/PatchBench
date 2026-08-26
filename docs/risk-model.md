# Risk Model

## Purpose

The risk model prioritizes the behavior a change may have disturbed. It is an auditable heuristic for proposing executable evidence, not a security verdict, correctness score, or substitute for execution.

## Deterministic signals

| Signal | Example risk | Typical contract |
|---|---|---|
| Public export, signature, or serialized response changes | Existing caller or client compatibility breaks | API compatibility |
| Cache, database, filesystem, or lifecycle mutation | Stale state, invalid transition, or failed cleanup | Stateful differential behavior |
| CLI parsing, stdout, exit-code, or output-file changes | Script and automation compatibility breaks | CLI contract |
| Authorization, redaction, logging, or secret-handling changes | Sensitive data or policy boundary violation | Policy or adversarial test |
| Error handling, retry, timeout, or concurrency changes | Failure-path or reliability regression | Stateful or repeated-run check |
| Dependency, configuration, container, or permission changes | Runtime, reproducibility, or isolation change | Policy, startup, or integration check |
| Test removal or assertion weakening | Visible coverage no longer establishes behavior | Preservation or replacement regression check |

## Risk finding record

Each deterministic finding must identify the changed path, relevant symbol or operation, category, change type, direct evidence, and confidence heuristic. PatchBench retains this record with the proposal so a reviewer can see why a check was suggested.

Confidence expresses how directly the patch evidence supports a hypothesis:

- `high`: a public interface or state transition changed and an affected caller, invariant, or direct operation is found.
- `medium`: a relevant mutation or behavior path changed but the dependent behavior needs review.
- `low`: naming or file-level context suggests a risk without a verified affected operation.

Confidence never establishes correctness and cannot change evaluation classification.

## Mapping to contracts

The model prefers contracts with observable outcomes. For example, a deleted cache invalidation calls for a before-and-after operation sequence; a changed CLI serializer calls for exact output and filesystem assertions; a public method signature change calls for a client-facing API scenario.

When no supported contract can express a finding, PatchBench records the coverage gap rather than fabricating a test or treating the finding as a failure.

## Limitations

Static signals can miss dynamic dispatch, generated code, external systems, implicit business rules, and emergent performance behavior. A high-confidence finding can still produce an irrelevant proposal, and a low-confidence finding can reveal a real regression. The accepted contract's executed evidence is therefore the only basis for a result.
