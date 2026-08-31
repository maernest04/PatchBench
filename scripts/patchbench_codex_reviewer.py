import json
import os
import subprocess
import sys
from pathlib import Path


repository = Path(os.environ["PATCHBENCH_REVIEWER_REPOSITORY"])
reviewer_root = repository.parent
public_directory = Path(os.environ["PATCHBENCH_REVIEWER_PUBLIC_DIR"])
candidate_patch = Path(os.environ["PATCHBENCH_REVIEWER_PATCH"])
output_path = Path(os.environ["PATCHBENCH_REVIEWER_OUTPUT"])
model = os.environ.get("PATCHBENCH_REVIEWER_MODEL")
schema_path = Path(__file__).resolve().parents[1] / "schemas" / "codex-reviewer-output.schema.json"
prompt = (
    "Review the candidate code change without modifying files. "
    f"The patched repository is {repository}. "
    f"The public task materials are {public_directory}. "
    f"The candidate patch is {candidate_patch}. "
    "Identify one concrete regression only when its category, affected paths or symbols, and rationale are supported by the public materials. "
    "Set outcome to finding for a concrete regression. Otherwise set outcome to no_finding, category to none, and use empty evidence lists."
)
result = subprocess.run(
    [
        "codex",
        "exec",
        "--ephemeral",
        "--skip-git-repo-check",
        "-C",
        str(reviewer_root),
        "--output-schema",
        str(schema_path),
        "-o",
        str(output_path),
    ]
    + (["--model", model] if model else [])
    + [prompt],
    check=False,
)
if result.returncode != 0:
    raise SystemExit(result.returncode)
raw_output = json.loads(output_path.read_text())
if raw_output["outcome"] == "no_finding":
    output_path.write_text("null")
else:
    raw_output.pop("outcome")
    output_path.write_text(json.dumps(raw_output))
