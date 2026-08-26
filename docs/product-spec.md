# Product Specification

## Problem

AI coding agents can produce changes that compile and pass visible tests while failing the requested behavior, violating a constraint, or breaking behavior that is only visible after a sequence of operations.

## Product statement

PatchBench is an execution-based benchmark that measures whether AI reviewers can detect and expose behavioral regressions in plausible AI-authored patches that pass visible tests. Its task-specific executable contracts establish ground truth; they do not serve as an LLM judge.

## Users

- Engineers and researchers evaluating AI code-review workflows.
- Teams deciding whether an AI reviewer provides evidence beyond a visible test suite.
- Developers studying the failure modes of AI-authored code changes.

## Inputs

- A versioned benchmark task.
- A repository and initial state.
- Public task materials and tests available to the agent.
- A plausible incorrect candidate patch that passes its public checks.
- A correct reference patch or independently verified expected behavior.
- Hidden evaluators and constraints available only to PatchBench.
- A reviewer-agent configuration, fixed prompt, and declared attempt budget.

## Outputs

- Candidate ground truth from the hidden executable contract.
- Structured reviewer findings and optional executable verification artifacts.
- Detection, executable-detection, false-positive, inconclusive, cost, and replay observations.
- Reproduction metadata and limitations for every experiment.

## Non-goals for the first release

- Proving arbitrary code universally correct or secure.
- Replacing human review for ambiguous requirements.
- Reducing an agent to one opaque quality score.
- Requiring an LLM provider or API key for the core evaluator.
- Allowing an LLM to declare a change correct without executed evidence.
- Claiming a general model ranking from a small or homogeneous corpus.
