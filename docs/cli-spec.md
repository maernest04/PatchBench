# CLI Specification

## Commands

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

## `patchbench codex-run`

```text
patchbench codex-run --task <task-directory> --prompt "<coding task>"
```

The command runs the installed Codex CLI against the task repository, then verifies Codex's working-tree changes through PatchBench before it returns.

## `patchbench agent-evaluate`

```text
PATCHBENCH_AGENT_COMMAND="your-agent-command" patchbench agent-evaluate --task <task-directory>
```

The command creates a temporary workspace containing only `repository/` and `public/`, then invokes the configured command with these environment variables:

- `PATCHBENCH_AGENT_REPOSITORY`
- `PATCHBENCH_AGENT_PUBLIC_DIR`
- `PATCHBENCH_AGENT_OUTPUT_PATCH`
- `PATCHBENCH_AGENT_MAX_ATTEMPTS`
- `PATCHBENCH_AGENT_MAX_TOOL_CALLS`
- `PATCHBENCH_AGENT_MAX_TOKENS`
- `PATCHBENCH_AGENT_MAX_COST_USD`

The command must write a unified diff to `PATCHBENCH_AGENT_OUTPUT_PATCH`. PatchBench evaluates that patch through the normal evaluator and stores only safe attempt metadata.

### Inspect a stored run

```text
patchbench show <run-id>
```

The command displays the task version, check results, classification, and replay guidance.

### Replay a stored run

```text
patchbench replay <run-id>
```

The command reconstructs the recorded environment and reruns the evaluation using the original task, patch, seed, and configuration.

### Report stored runs

```text
patchbench report
```

The command aggregates stored candidate-evaluation results. It does not yet report reviewer-benchmark outcomes.

## Exit codes

- `0`: `PASS`
- `1`: `FAIL`
- `2`: invalid invocation, invalid task, invalid patch, or setup error before evaluation begins
- `3`: `INCONCLUSIVE`

## Output requirements

`evaluate`, `verify-working-tree`, `codex-run`, `agent-evaluate`, `show`, `replay`, and `report` support readable terminal output or `--format json`.

## Non-goals

The current CLI does not yet include reviewer-benchmark commands, an interactive shell, web dashboard, agent-management commands, or remote execution commands.
