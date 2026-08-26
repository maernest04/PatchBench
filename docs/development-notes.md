# Development Notes

## 2026-08-24: Project initialization

- PatchBench evaluates AI coding agents through execution, not an LLM quality score.
- It supports any software task with a task-specific executable contract.
- Python and pytest fixtures are an initial implementation choice, not a permanent product boundary.
- Core evaluation works without an API key; real-agent adapters are optional later integrations.
- Results report correctness, preservation, safety, reliability, and efficiency separately.

## 2026-08-25: First vertical slice

- Added the cache-invalidation fixture with public cache-behavior tests and a hidden deletion regression test.
- Added correct and stale-cache candidate patches. Both pass visible tests; only the correct patch passes hidden behavior checks.
- Added a Python CLI, task loader, candidate workspace manager, Docker runner boundary, evaluator, and text/JSON reporter.
- Added unit and integration tests for task loading, safe patch application, evaluator classification, Docker-daemon unavailability, and fixture behavior.
- Docker is installed and the containerized evaluator path is end-to-end verified.

## 2026-08-25: Container proof and evidence storage

- Added CPU limits to task contracts and Docker execution.
- Added a filesystem-backed run store that snapshots the task and candidate patch, stores per-check stdout and stderr, and records JSON metadata.
- Added `show` and `replay` CLI commands. Replays create linked run records.
- Verified a passing candidate in Docker, then replayed it with the same `PASS` classification.
- Verified a stale-cache candidate passes public tests, fails the hidden test in Docker, and retains the hidden pytest output as evidence.

## 2026-08-25: Differential preservation proof

- Added a hidden differential scenario that runs the same deletion-and-read sequence against the baseline and candidate workspaces.
- The scenario serializes normalized observations, allowing PatchBench to block a candidate when it changes established behavior.
- Verified in Docker that the correct patch passes all three checks and the stale-cache patch fails both hidden checks despite passing the public check.

## 2026-08-25: Evaluator quality coverage

- Added checks for malformed task contracts, unsafe and unapplicable patches, command timeouts, unavailable Docker, runner crashes, output normalization, reporting, workspace cleanup, and hidden-material isolation.
- Added Docker integration coverage for both fixture candidates, with a clean skip when the local daemon is unavailable.
- Added an evaluator quality ledger for recording suspected false positives and false negatives.

## 2026-08-25: CLI contract

- Added a CLI evaluator that verifies a command's exit code, exact stdout, and declared output files in an isolated temporary directory.
- Added the CLI report-generation fixture, where a superficial candidate passes the public slug-output contract but fails the hidden JSON file contract.

## 2026-08-25: Expanded task contracts

- Added an API compatibility evaluator that compares a scenario's normalized JSON observation with its declared output contract.
- Added API compatibility, refactor-preservation, and secret-redaction-policy fixtures with correct and intentionally incorrect candidates.
- Documented evidence requirements for future frontend, mobile, performance, and infrastructure evaluators.

## 2026-08-25: Agent adapter foundation

- Added a provider-neutral adapter contract and an environment-configured command adapter.
- The adapter copies only repository and public materials into a temporary agent workspace, then returns one candidate patch for normal evaluation.
- Agent runs persist only safe adapter metadata and declared budgets; command output and environment variables are not captured.
- A configured real coding-agent command is still required to complete the end-to-end Phase 6 validation.

## 2026-08-25: Real Codex agent validation

- Added a Codex CLI bridge that runs an authenticated local Codex attempt inside the temporary public agent workspace and derives a unified patch from its changes.
- Verified one real Codex attempt on `cache-invalidation-v1`; the generated patch passed public, hidden, and differential checks through the normal evaluator path.

## 2026-08-25: Benchmark reporting foundation

- Added stored-run aggregation for task success, hidden failures, safety violations, inconclusives, runtime, and replay reproducibility.
- Reports separate fixture and agent sources and state when no real-agent attempts or replay pairs are present.

## 2026-08-25: First real-agent benchmark

- Ran three local Codex attempts across each of the five current task fixtures, then replayed one result per task.
- The versioned result reports 80% task success, 20% hidden failures, no inconclusives, and complete replay agreement.

## Note format

Add dated entries for experiments, observed failure modes, rejected approaches, benchmark changes, and open questions. Promote significant, difficult-to-reverse choices to a decision record.
