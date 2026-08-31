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

## `patchbench review-evaluate`

```text
PATCHBENCH_REVIEWER_COMMAND="your-reviewer-command" patchbench review-evaluate --task <task-directory> --patch <candidate.patch> --experiment <experiment.yaml>
```

The command accepts a task-registered candidate patch, applies it in a temporary reviewer workspace, then copies only the patched repository, public task materials, and candidate patch. The reviewer receives `PATCHBENCH_REVIEWER_REPOSITORY`, `PATCHBENCH_REVIEWER_PUBLIC_DIR`, `PATCHBENCH_REVIEWER_PATCH`, `PATCHBENCH_REVIEWER_OUTPUT`, and its declared tool, token, and cost budgets.

The reviewer writes either `null` or a JSON finding containing `category`, `affected_paths`, `affected_symbols`, and `rationale`. PatchBench stores and prints `DETECTED`, `MISSED`, `FALSE_POSITIVE`, `CORRECT_REJECTION`, or `INCONCLUSIVE`.

Use the included Codex bridge by setting `PATCHBENCH_REVIEWER_COMMAND` to `python3` followed by the absolute path to `scripts/patchbench_codex_reviewer.py`. The bridge uses `codex exec` with a JSON schema and writes only Codex's final structured response to the reviewer output path.

When `--experiment` is supplied, its task list, reviewer adapter, model, prompt version, and budgets are validated and stored with the review. Each immutable manifest names one exact pilot configuration.

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

The command aggregates stored candidate-evaluation results.

### Report stored reviews

```text
patchbench review-report
```

The command aggregates stored reviewer outcomes overall and by task, and retains each review attempt in the output. Rates describe only the stored attempts; they do not make a general model-performance claim.

Use `--experiment-id <id>` to report only the attempts from one frozen experiment.

## Exit codes

- `0`: `PASS`
- `1`: `FAIL`
- `2`: invalid invocation, invalid task, invalid patch, or setup error before evaluation begins
- `3`: `INCONCLUSIVE`

## Output requirements

`evaluate`, `verify-working-tree`, `codex-run`, `agent-evaluate`, `review-evaluate`, `show`, `replay`, `report`, and `review-report` support readable terminal output or `--format json`.

## Non-goals

The current CLI does not yet include an interactive shell, web dashboard, agent-management commands, or remote execution commands.
