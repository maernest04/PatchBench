import pytest

from export import export_items


def test_failed_replacement_preserves_existing_output(monkeypatch, tmp_path):
    output = tmp_path / "items.json"
    output.write_text('["previous"]\n')

    def fail_replace(source, destination):
        raise OSError("replacement failed")

    monkeypatch.setattr("pathlib.Path.replace", fail_replace)

    with pytest.raises(OSError, match="replacement failed"):
        export_items(["current"], output)

    assert output.read_text() == '["previous"]\n'
