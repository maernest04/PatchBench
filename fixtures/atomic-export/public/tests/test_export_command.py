import json
import subprocess
import sys


def test_export_command_writes_json_array(tmp_path):
    output = tmp_path / "items.json"

    result = subprocess.run(
        [sys.executable, "export.py", "alpha", "beta", "--output", str(output)],
        capture_output=True,
        text=True,
        check=True,
    )

    assert result.stdout == ""
    assert json.loads(output.read_text()) == ["alpha", "beta"]
