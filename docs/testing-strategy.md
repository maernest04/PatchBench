# Testing Strategy

## Objective

PatchBench must test both candidate code and the evaluator itself. A passing PatchBench test suite is not enough; fixtures must demonstrate that the evaluator accepts correct changes and rejects meaningful incorrect ones.

## Test layers

### Unit tests

Test task parsing, schema validation, patch validation, result classification, output normalization, evidence serialization, and report formatting without running containers.

### Integration tests

Test temporary workspaces, patch application, Docker execution, resource limits, public checks, hidden checks, local persistence, and cleanup behavior.

### End-to-end tests

Evaluate complete fixtures through the CLI. Verify terminal output, JSON output, run storage, and replay behavior.

## Evaluator-validation matrix

Every fixture should eventually include:

| Candidate | Public checks | Hidden checks | Expected classification |
|---|---:|---:|---|
| Correct patch | Pass | Pass | `PASS` |
| Obvious broken patch | Fail | Fail or not reached | `FAIL` |
| Hidden-regression patch | Pass | Fail | `FAIL` |
| Evaluator/environment failure | N/A | N/A | `INCONCLUSIVE` |

## Required negative cases

- Malformed task contract.
- Patch that cannot be applied.
- Test command timeout.
- Container startup failure.
- Hidden-check crash.
- Missing required run artifact.
- Attempt to access hidden files from an agent-visible workspace.
- Nondeterministic result in a task declared deterministic.

## Repeatability

For deterministic fixtures, run the same candidate repeatedly with the same seed and environment. Classification changes are evaluator defects until explained.

## Measurement discipline

Track evaluator false positives, false negatives, inconclusive results, and execution failures. Do not advertise a detection rate without reporting the fixture set and these failure categories.

