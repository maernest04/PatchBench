# Evaluator Extension Points

Each evaluator type uses the same task loader, isolated candidate workspace, Docker runner, evidence model, reporter, and run store. A new type adds only a task-contract schema and a deterministic runner method that turns observable execution into a `CommandResult`.

| Domain | Contract evidence |
| --- | --- |
| Frontend | Browser-visible DOM state, accessibility tree, screenshots, and network policy results. |
| Mobile | Emulator interactions, rendered state, permissions, and persisted data. |
| Performance | Fixed workload, elapsed time, memory ceiling, and deterministic baseline comparison. |
| Infrastructure | Plan output, policy checks, isolated deployment simulation, and declared resource changes. |

Each contract must define public and hidden materials, deterministic pass/fail conditions, isolation requirements, and when an environment problem requires `INCONCLUSIVE`.
