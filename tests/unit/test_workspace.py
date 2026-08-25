from pathlib import Path

import pytest

from patchbench.workspace import create_candidate_workspace


@pytest.mark.parametrize(
    "patch_name",
    ["correct.patch", "stale-cache.patch"],
)
def test_applies_fixture_patch(patch_name):
    fixture = Path("fixtures/cache-invalidation")

    with create_candidate_workspace(fixture / "repository", fixture / "candidates" / patch_name) as temporary_directory:
        source = (Path(temporary_directory) / "repository" / "user_store.py").read_text()

    assert "self._cache = {}" in source
