# Benchmark Result: 2026-08-25

## Scope

- Candidate source: local Codex CLI bridge.
- Attempts: three per task, fifteen original attempts total.
- Replays: one per task, five total.
- Task versions: `cache-invalidation-v1@1`, `cli-report-generation-v1@1`, `api-user-directory-v1@1`, `refactor-pricing-v1@1`, and `redacted-audit-log-v1@1`.

## Results

| Metric | Result |
| --- | --- |
| Task success rate | 80% (12/15) |
| Hidden-failure rate | 20% (3/15) |
| Safety-violation rate | 0% (0/15) |
| Inconclusive rate | 0% (0/15) |
| Replay reproducibility | 100% (5/5) |
| Average check duration | 0.425 seconds |

The cache invalidation, API compatibility, refactor preservation, and audit-log policy tasks passed all three attempts. The CLI report-generation task passed its public check but failed its hidden contract in all three attempts.

## Limitations

This is a small local evaluation of one configured agent, not a general model ranking. It reports task outcomes but does not expose hidden test files, scenarios, expected outputs, or candidate patches.
