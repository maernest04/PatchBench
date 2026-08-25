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
- Docker is installed but its daemon is not running locally, so the containerized evaluator path is implemented but not yet end-to-end verified.

## Note format

Add dated entries for experiments, observed failure modes, rejected approaches, benchmark changes, and open questions. Promote significant, difficult-to-reverse choices to a decision record.
