import subprocess

import pytest

from patchbench.runner import DockerRunner


@pytest.fixture(scope="session")
def docker_runner():
    available = subprocess.run(["docker", "info"], capture_output=True, text=True, check=False)
    if available.returncode != 0:
        pytest.skip("Docker daemon is unavailable")
    return DockerRunner()
