from pathlib import Path

import pytest

from patchbench.workspace import PatchApplicationError, create_candidate_workspace, validate_patch


@pytest.mark.parametrize(
    "patch_name",
    ["correct.patch", "stale-cache.patch"],
)
def test_applies_fixture_patch(patch_name):
    fixture = Path("fixtures/cache-invalidation")

    with create_candidate_workspace(fixture / "repository", fixture / "candidates" / patch_name) as temporary_directory:
        source = (Path(temporary_directory) / "repository" / "user_store.py").read_text()

    assert "self._cache = {}" in source


def test_rejects_patch_path_outside_workspace(tmp_path):
    patch = tmp_path / "unsafe.patch"
    patch.write_text("--- a/../outside.py\n+++ b/../outside.py\n")

    with pytest.raises(ValueError, match="patch contains unsafe path"):
        validate_patch(patch)


def test_candidate_workspace_excludes_hidden_task_material():
    fixture = Path("fixtures/cache-invalidation")

    with create_candidate_workspace(fixture / "repository", fixture / "candidates" / "correct.patch") as temporary_directory:
        workspace = Path(temporary_directory) / "repository"
        assert not (workspace / "hidden").exists()


def test_rejects_unapplicable_patch(tmp_path):
    fixture = Path("fixtures/cache-invalidation")
    patch = tmp_path / "invalid.patch"
    patch.write_text("--- a/user_store.py\n+++ b/user_store.py\n@@ -1 +1 @@\n-missing\n+replacement\n")

    with pytest.raises(PatchApplicationError, match="patching file user_store.py"):
        create_candidate_workspace(fixture / "repository", patch)
