# Benchmark Reporting

Run `patchbench report` to aggregate stored evaluation results. The report groups runs by versioned task and reports task success, hidden failures, safety violations, inconclusives, average check duration, and replay reproducibility separately.

```text
patchbench report --artifacts-dir artifacts/runs --format json
```

Reports distinguish fixture from agent-sourced runs using safe stored metadata. They always include limitations: a collection of local fixture runs is not a general model ranking, and missing agent attempts or replay pairs are stated explicitly.

Benchmark reports are versioned independently from task versions. Add a new report version whenever aggregation semantics change, and preserve task/evaluator limitations alongside metrics.
