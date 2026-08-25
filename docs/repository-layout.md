# Repository Layout

```text
PatchBench/
├── README.md
├── AGENTS.md
├── pyproject.toml
├── .gitignore
├── docs/
├── schemas/
├── src/
│   └── patchbench/
│       ├── evaluators/
│       ├── adapters/
│       └── storage/
├── fixtures/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── end_to_end/
└── scripts/
```

## Root files

- `README.md`: project purpose, scope, and quick-start guidance.
- `AGENTS.md`: development and evaluation-integrity rules.
- `pyproject.toml`: Python package metadata, tool configuration, and test configuration. It is added when implementation begins.
- `.gitignore`: excludes environments, run artifacts, credentials, and generated reports. It is added when implementation begins.

## `src/patchbench/`

Contains the provider-independent evaluation engine.

- `cli.py`: command-line interface.
- `models.py`: task, run, check-result, evidence, and classification models.
- `task_loader.py`: task-contract loading and schema validation.
- `workspace.py`: clean baseline and candidate workspace creation.
- `runner.py`: controlled command and container execution.
- `evaluator.py`: evaluator orchestration.
- `evidence.py`: evidence assembly and classification support.
- `replay.py`: run reconstruction and replay.
- `reporter.py`: human-readable and JSON reports.

Subdirectories are reserved for focused extension points:

- `evaluators/`: pytest, command, differential, and future task-specific evaluators.
- `adapters/`: optional real-agent integrations. This stays empty until Phase 6.
- `storage/`: local run-history persistence. This stays empty until Phase 3.

## `schemas/`

Contains versioned JSON schemas for task contracts, run records, and result records. Schemas are the compatibility boundary between benchmark tasks, evaluator code, and reports.

## `fixtures/`

Contains versioned benchmark tasks. Each fixture owns its public materials, hidden checks, source repository, candidate patches, and task contract. Fixture tests are not the same as PatchBench's own tests.

## `tests/`

Tests PatchBench itself.

- `unit/`: isolated model, parser, normalization, and classification tests.
- `integration/`: workspace, Docker, evaluator, and persistence tests.
- `end_to_end/`: complete fixture evaluation and replay tests.

## `scripts/`

Contains developer-only helpers that simplify local fixture execution or report generation. Scripts must not become a second production implementation path.

