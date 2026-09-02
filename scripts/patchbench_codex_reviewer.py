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
prompt_version = os.environ.get("PATCHBENCH_REVIEWER_PROMPT_VERSION", "codex-reviewer-v1")
schema_path = Path(__file__).resolve().parents[1] / "schemas" / "codex-reviewer-output.schema.json"
prompt_path = Path(__file__).resolve().parents[1] / "prompts" / f"{prompt_version}.txt"
prompt = prompt_path.read_text().format(
    repository=repository,
    public_directory=public_directory,
    candidate_patch=candidate_patch,
    verification_instruction=(
        "Provide a verification_command that returns non-zero for the candidate and zero for the control."
        if os.environ.get("PATCHBENCH_REVIEWER_WORKFLOW") == "executable_evidence"
        else "Do not provide a verification_command."
    ),
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
