# CLI Specification

## V1 commands

### Evaluate a candidate patch

```text
patchbench evaluate --task <task-directory> --patch <candidate.patch>
```

The command validates the task and patch, creates isolated workspaces, runs every enabled check, writes a run record, and prints a concise result.

## `patchbench verify-working-tree`

```text
patchbench verify-working-tree --task <task-directory>
```

The command collects tracked and untracked changes from the task repository's Git working tree, evaluates the resulting unified patch through the normal evaluator, and stores the result. A clean working tree is `INCONCLUSIVE`, because there is no candidate change to verify.

### Inspect a stored run

```text
patchbench show <run-id>
```

The command displays the task version, candidate digest, check results, findings, and replay guidance.

### Replay a stored run

```text
patchbench replay <run-id>
```

The command reconstructs the recorded environment and reruns the evaluation using the original task, patch, seed, and configuration.

## Exit codes

- `0`: `PASS`
- `1`: `FAIL`
- `2`: invalid invocation, invalid task, invalid patch, or setup error before evaluation begins
- `3`: `INCONCLUSIVE`

## Output requirements

Every command supports a readable terminal summary. `evaluate` and `show` must also support JSON output before any external automation or agent adapter relies on them.

## Non-goals

V1 does not include an interactive shell, web dashboard, agent-management commands, or remote execution commands.
