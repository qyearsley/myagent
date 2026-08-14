"""Tests for reading, writing, and listing files inside the sandbox."""

from functions.get_file_content import get_file_content
from functions.get_files_info import get_files_info
from functions.write_file import write_file
import pytest


class TestGetFileContent:
    def test_returns_the_whole_file_when_it_fits(self, sandbox):
        assert get_file_content(str(sandbox), "main.py") == "print('hello')\n"

    def test_truncates_a_long_file_and_says_so(self, sandbox, monkeypatch):
        # MAX_CHARS is imported by value at module scope, so patch it there
        # rather than on config.
        monkeypatch.setattr("functions.get_file_content.MAX_CHARS", 10)
        (sandbox / "long.txt").write_text("a" * 50)

        result = get_file_content(str(sandbox), "long.txt")

        assert result.startswith("a" * 10)
        assert "truncated at 10 characters" in result

    def test_leaves_a_file_exactly_at_the_limit_untruncated(self, sandbox, monkeypatch):
        monkeypatch.setattr("functions.get_file_content.MAX_CHARS", 10)
        (sandbox / "exact.txt").write_text("a" * 10)
        assert get_file_content(str(sandbox), "exact.txt") == "a" * 10

    def test_reports_a_missing_file(self, sandbox):
        assert "File not found" in get_file_content(str(sandbox), "nope.txt")

    def test_reports_a_directory(self, sandbox):
        assert "not a regular file" in get_file_content(str(sandbox), "pkg")


class TestWriteFile:
    def test_creates_a_new_file(self, sandbox):
        result = write_file(str(sandbox), "new.txt", "content")
        assert "Successfully wrote" in result
        assert (sandbox / "new.txt").read_text() == "content"

    def test_overwrites_an_existing_file(self, sandbox):
        write_file(str(sandbox), "main.py", "replaced")
        assert (sandbox / "main.py").read_text() == "replaced"

    def test_creates_missing_parent_directories(self, sandbox):
        write_file(str(sandbox), "a/b/c.txt", "deep")
        assert (sandbox / "a" / "b" / "c.txt").read_text() == "deep"

    def test_refuses_to_overwrite_a_directory(self, sandbox):
        assert "is a directory" in write_file(str(sandbox), "pkg", "content")
        assert (sandbox / "pkg").is_dir()


class TestGetFilesInfo:
    def test_lists_entries_with_size_and_directory_flag(self, sandbox):
        result = get_files_info(str(sandbox), ".")
        size = (sandbox / "main.py").stat().st_size
        assert f"main.py: file_size={size} bytes, is_dir=False" in result
        assert "pkg: " in result
        assert "is_dir=True" in result

    def test_lists_a_subdirectory(self, sandbox):
        assert "util.py" in get_files_info(str(sandbox), "pkg")

    def test_reports_a_file_as_not_a_directory(self, sandbox):
        assert "is not a directory" in get_files_info(str(sandbox), "main.py")

    @pytest.mark.parametrize("directory", [".", "pkg"])
    def test_never_reports_absolute_paths_to_the_model(self, sandbox, directory):
        # Leaking the host layout is both noise and information the model
        # does not need.
        assert str(sandbox) not in get_files_info(str(sandbox), directory)
