# Agent Adapters

PatchBench accepts agent-generated patches through a provider-neutral `AgentAdapter` contract. The initial `CommandAgentAdapter` uses `PATCHBENCH_AGENT_COMMAND` to invoke a locally configured coding-agent command.

## Agent-visible inputs

For each attempt, PatchBench creates a temporary directory containing only:

- `repository/`: a writable copy of the task repository.
- `public/`: public task instructions and public checks, when present.

Hidden checks, candidate fixtures, evaluator source, and stored evidence are not copied into this directory.

## Command environment

The configured command receives:

- `PATCHBENCH_AGENT_REPOSITORY`
- `PATCHBENCH_AGENT_PUBLIC_DIR`
- `PATCHBENCH_AGENT_OUTPUT_PATCH`
- `PATCHBENCH_AGENT_MAX_ATTEMPTS`
- `PATCHBENCH_AGENT_MAX_TOOL_CALLS`
- `PATCHBENCH_AGENT_MAX_TOKENS`
- `PATCHBENCH_AGENT_MAX_COST_USD`

It must write one unified diff to `PATCHBENCH_AGENT_OUTPUT_PATCH` and exit with status `0`.

## Run command

```text
PATCHBENCH_AGENT_COMMAND="your-agent-command" patchbench agent-evaluate --task fixtures/cache-invalidation
```

`agent-evaluate` gives the attempt a fixed wall-clock timeout and passes the remaining declared budgets to the adapter command. PatchBench does not capture the command's stdout, stderr, environment variables, or credentials. It stores only the generated patch and safe attempt metadata before evaluating the patch through the normal evaluator.

## Codex CLI bridge

The repository includes `scripts/patchbench_codex_agent.py`, which invokes an installed, logged-in Codex CLI inside the temporary agent workspace and creates a unified diff from its changes.

```text
PATCHBENCH_AGENT_COMMAND="python3 scripts/patchbench_codex_agent.py" patchbench agent-evaluate --task fixtures/cache-invalidation
```
