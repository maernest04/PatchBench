import os
import shutil
import subprocess
import sys
from pathlib import Path


repository = Path(os.environ["PATCHBENCH_AGENT_REPOSITORY"])
agent_root = repository.parent
baseline = agent_root / "baseline"
output_patch = Path(os.environ["PATCHBENCH_AGENT_OUTPUT_PATCH"])
public_directory = Path(os.environ["PATCHBENCH_AGENT_PUBLIC_DIR"])
shutil.copytree(repository, baseline)
prompt = (
    "Implement the task using only the repository and public materials. "
    f"Public materials are in {public_directory}. "
    "Modify the repository in place, preserve existing behavior unless the public task says otherwise, "
    "and do not access files outside the repository or public-material directory."
)
result = subprocess.run(
    [
        "codex",
        "exec",
        "--ephemeral",
        "--sandbox",
        "workspace-write",
        "--skip-git-repo-check",
        "-C",
        str(repository),
        prompt,
    ],
    check=False,
)
if result.returncode != 0:
    raise SystemExit(result.returncode)
diff = subprocess.run(
    ["diff", "-ruN", "baseline", "repository"],
    cwd=agent_root,
    capture_output=True,
    text=True,
    check=False,
)
if diff.returncode not in {0, 1}:
    raise SystemExit(diff.returncode)
output_patch.write_text(diff.stdout)
