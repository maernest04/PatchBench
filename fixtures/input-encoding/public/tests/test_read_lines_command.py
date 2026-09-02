import subprocess
import sys


def test_read_lines_command_prints_ascii_file(tmp_path):
    input_path = tmp_path / "input.txt"
    input_path.write_text("first\nsecond\n", encoding="ascii")

    result = subprocess.run(
        [sys.executable, "read_lines.py", str(input_path)],
        capture_output=True,
        text=True,
        check=True,
    )

    assert result.stdout == "first\nsecond\n"
