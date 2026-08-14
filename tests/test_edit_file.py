"""Tests for edit_file's exactly-one-occurrence contract.

A failed edit must leave the file untouched -- a partial write would corrupt
whatever the agent was working on.
"""

from functions.edit_file import edit_file

ORIGINAL_MAIN = "print('hello')\n"


def test_replaces_a_unique_occurrence(sandbox):
    result = edit_file(str(sandbox), "main.py", "hello", "goodbye")
    assert "Successfully edited" in result
    assert (sandbox / "main.py").read_text() == "print('goodbye')\n"


def test_refuses_when_the_string_is_absent(sandbox):
    result = edit_file(str(sandbox), "main.py", "not-in-the-file", "x")
    assert "not found" in result
    assert (sandbox / "main.py").read_text() == ORIGINAL_MAIN


def test_refuses_when_the_string_is_ambiguous(sandbox):
    duplicated = "x = 1\nx = 1\n"
    (sandbox / "dup.py").write_text(duplicated)
    result = edit_file(str(sandbox), "dup.py", "x = 1", "x = 2")
    assert "must be unique" in result
    assert (sandbox / "dup.py").read_text() == duplicated


def test_refuses_a_file_that_does_not_exist(sandbox):
    assert "does not exist" in edit_file(str(sandbox), "nope.py", "a", "b")


def test_refuses_a_directory(sandbox):
    assert "does not exist or is not a regular file" in edit_file(str(sandbox), "pkg", "a", "b")
