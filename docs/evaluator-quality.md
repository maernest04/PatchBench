# Evaluator Quality Ledger

## Known fixture cases

| Case | Expected classification | Purpose |
| --- | --- | --- |
| Correct cache invalidation patch | `PASS` | Confirms valid behavior is accepted. |
| Stale-cache patch | `FAIL` | Confirms a public-test-only patch is blocked by hidden and differential checks. |
| Missing or unsafe patch | `INCONCLUSIVE` | Separates invalid evaluator input from a verified candidate defect. |
| Docker unavailable or runner crash | `INCONCLUSIVE` | Separates evaluator infrastructure failures from candidate failures. |

## False-result policy

Record every suspected false positive or false negative here with its task version, observed evidence, root cause, and follow-up fixture or evaluator change. No known false positives or false negatives have been observed for `cache-invalidation-v1`.
