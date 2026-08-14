"""Shared fixtures for the myagent tests.

Every tool takes the sandbox working directory as its first argument, so the
tests build a small throwaway project and point the tools at it.
"""

import pytest


@pytest.fixture
def sandbox(tmp_path):
    """The agent's permitted working directory, laid out like a small project."""
    working_dir = tmp_path / "sandbox"
    working_dir.mkdir()
    (working_dir / "main.py").write_text("print('hello')\n")
    (working_dir / "pkg").mkdir()
    (working_dir / "pkg" / "util.py").write_text("VALUE = 1\n")
    return working_dir


@pytest.fixture
def outside(tmp_path):
    """A directory beside the sandbox that the agent must never reach."""
    path = tmp_path / "outside"
    path.mkdir()
    (path / "secret.txt").write_text("SECRET\n")
    return path
