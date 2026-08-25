# Benchmark Specification

## Goal

The benchmark measures whether AI coding agents complete software tasks using executable evidence instead of visible-test success alone.

## Task composition

Each task includes:

- A small repository and reproducible initial state.
- A task description and public materials available to the agent.
- Public tests or observable checks when appropriate.
- Hidden acceptance checks and constraints.
- A documented evaluation environment and resource limits.
- An independently verified expected outcome.

## Initial fixture strategy

The first fixtures use Python and pytest because they make the core evaluator easy to validate. They are examples, not a product boundary.

Initial categories may include:

- Backend state and lifecycle behavior.
- CLI and library behavior.
- API compatibility and error semantics.
- Security and authorization constraints.
- Refactors that must preserve behavior.

## Task quality requirements

- One primary task objective.
- Clear expected behavior or explicit constraints.
- At least one evaluator beyond visible tests where practical.
- A correct reference solution or independently verified expected result.
- A deliberately incorrect candidate for testing the evaluator when feasible.
- No secrets, external network dependency, or unmanaged nondeterminism.

## Leakage rules

- Agents access only public materials.
- Hidden tests, hidden expected outcomes, and reference solutions remain isolated from agent execution.
- Benchmark documentation must not reveal task-specific hidden conditions.

## Versioning

Tasks and evaluators are immutable once released. A change creates a new benchmark version so results remain comparable over time.

