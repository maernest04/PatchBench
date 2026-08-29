# Implementation Plan

## Completed foundation

PatchBench can apply a unified diff to an isolated Docker workspace, run public and hidden pytest, differential, CLI, API, and policy checks, classify results as `PASS`, `FAIL`, or `INCONCLUSIVE`, and retain replayable evidence. It includes six Python fixtures, candidate-generating and reviewer adapters, working-tree verification, Codex integration, and stored run and reviewer reporting.

## Phase 8: Reviewer-regression corpus

### Goal

Create a curated corpus of plausible incorrect patches that pass visible tests but fail one clear hidden behavioral contract. The corpus is the benchmark's central artifact; the existing evaluator establishes each task's ground truth.

### Phase 8A: Corpus contract and pilot

- [x] Define a reviewer-finding schema and private ground-truth labels for the first task.
- [x] Define task authoring rules: one primary hidden regression, one correct reference, one plausible incorrect candidate, and public-test-pass proof.
- [x] Build a six-task pilot spanning state/lifecycle, API compatibility, CLI/filesystem behavior, redaction/authorization, refactor preservation, and reliability/error paths.
- [ ] Record per-task author rationale, candidate plausibility review, deterministic environment, and hidden-evaluator evidence without leaking the fault to reviewer agents.
- [x] Register control and known-regression candidates for each pilot task.
- [ ] Validate each pilot task against its incorrect candidate, correct reference, and at least one irrelevant reviewer finding.

### Phase 8B: Corpus expansion and quality

- [ ] Expand to 15–25 tasks with at least three tasks per major category.
- [ ] Include both human-authored and observed AI-style failure patterns; label provenance accurately.
- [ ] Add task-level difficulty and confound review to avoid trivial test-name, diff-size, or naming leaks.
- [ ] Add a correct-reference and incorrect-candidate replay check to the corpus release process.
- [ ] Version and freeze the first corpus release before running comparison experiments.

### Exit criterion

At least six pilot tasks each prove that the incorrect candidate passes public checks, fails a hidden contract, and can be replayed; no public material reveals the task's fault label.

## Phase 9: Reviewer-agent evaluation harness

### Goal

Measure whether an AI reviewer identifies the corpus's known regression without receiving hidden information.

### Checklist

- [x] Define a structured reviewer finding with category, affected paths or symbols, and rationale.
- [x] Define a provider-neutral reviewer adapter with fixed time, tool, token, and cost budgets.
- [x] Build a public-only reviewer workspace containing the repository, task, public tests, and incorrect candidate patch.
- [x] Add a Codex reviewer bridge that produces schema-conforming findings.
- [x] Implement deterministic scoring against pre-authored ground-truth fault labels.
- [ ] Validate executable artifacts by running them against the incorrect candidate and correct reference or baseline as appropriate.
- [ ] Classify detection, executable detection, miss, false positive, and inconclusive independently.
- [ ] Preserve prompt version, safe adapter metadata, artifacts, scorer output, and replay data.

### Exit criterion

One reviewer adapter completes the six-task pilot without hidden-material access, and scorer tests cover correct detection, wrong detection, executable detection, false positive, and infrastructure inconclusive outcomes.

## Phase 10: Controlled comparison and report

### Goal

Produce transparent evidence of what reviewer workflows add beyond public tests and text-only review.

### Checklist

- [ ] Freeze a fixed reviewer prompt, model configuration, tools, budgets, and attempt count before each experiment.
- [ ] Run a public-test baseline, text-only reviewer baseline, and executable-evidence reviewer workflow over the frozen corpus.
- [ ] Run at least three independent attempts per task and workflow where cost permits.
- [ ] Report detection, executable-detection, false-positive, inconclusive, runtime, cost, and replay metrics by category and task.
- [ ] Publish per-task evidence and explicit threats to validity without publishing active hidden checks.
- [ ] State that results apply only to the named corpus, reviewer configurations, and experiment date.

### Exit criterion

A versioned report compares the three workflows on the frozen corpus, includes raw per-task outcomes and replay evidence, and makes no unsupported general ranking claim.

## Deferred work

- Web UI.
- Hosted or multi-tenant execution.
- Arbitrary-language support.
- Automated change-contract generation.
- Autonomous patch repair.
- Broad model rankings from insufficient task samples.
