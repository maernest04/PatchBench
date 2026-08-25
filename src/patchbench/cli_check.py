import json
import subprocess
import sys
from pathlib import Path


expectation = json.loads(sys.argv[1])
result = subprocess.run(expectation["command"], capture_output=True, text=True, check=False)
observed_files = {}
for path in expectation["files"]:
    file_path = Path("/tmp/patchbench-output") / path
    observed_files[path] = file_path.read_text() if file_path.is_file() else None
payload = {
    "command": list(expectation["command"]),
    "expected": {
        "exit_code": expectation["exit_code"],
        "stdout": expectation["stdout"],
        "files": expectation["files"],
    },
    "observed": {
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "files": observed_files,
    },
}
print(json.dumps(payload, sort_keys=True))
matches = (
    result.returncode == expectation["exit_code"]
    and result.stdout == expectation["stdout"]
    and observed_files == expectation["files"]
)
raise SystemExit(0 if matches else 1)
