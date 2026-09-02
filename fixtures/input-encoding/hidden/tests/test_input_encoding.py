from read_lines import read_lines


def test_read_lines_decodes_utf8_content(tmp_path):
    input_path = tmp_path / "input.txt"
    input_path.write_bytes("café\n東京\n".encode("utf-8"))

    assert read_lines(input_path) == ["café", "東京"]
