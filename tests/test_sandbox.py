"""Tests for the sandbox boundary -- the security-relevant part of the agent.

Every tool resolves its path argument through `validate_path`, which is what
stops the model from reading or writing outside its working directory. These
tests exercise that boundary directly and then through each tool.
"""

from functions.edit_file import edit_file
from functions.get_file_content import get_file_content
from functions.get_files_info import get_files_info
from functions.helpers import validate_path
from functions.run_python_file import run_python_file
from functions.search_files import search_files
from functions.write_file import write_file
import pytest

REFUSAL = "outside the permitted working directory"


class TestValidatePath:
    @pytest.mark.parametrize(
        "path",
        [
            "../outside/secret.txt",
            "../../etc/hosts",
            "/etc/hosts",
            "pkg/../../outside/secret.txt",
        ],
    )
    def test_rejects_paths_that_leave_the_working_directory(self, sandbox, outside, path):
        with pytest.raises(Exception, match=REFUSAL):
            validate_path(sandbox, path)

    def test_rejects_a_symlink_pointing_out_of_the_sandbox(self, sandbox, outside):
        """A symlink is a real escape route: the path looks contained but isn't.

        String-level normalisation cannot see through links, so validate_path
        has to resolve them before comparing.
        """
        (sandbox / "link").symlink_to(outside)
        with pytest.raises(Exception, match=REFUSAL):
            validate_path(sandbox, "link/secret.txt")

    def test_rejects_a_sibling_directory_that_shares_a_name_prefix(self, sandbox, tmp_path):
        """`sandbox-evil` must not count as being inside `sandbox`."""
        (tmp_path / "sandbox-evil").mkdir()
        with pytest.raises(Exception, match=REFUSAL):
            validate_path(sandbox, "../sandbox-evil")

    @pytest.mark.parametrize(
        "path",
        [".", "main.py", "pkg", "pkg/util.py", "pkg/../main.py", "new/nested/file.txt"],
    )
    def test_allows_paths_inside_the_working_directory(self, sandbox, path):
        # The last case does not exist yet -- write_file relies on that working.
        assert validate_path(sandbox, path).startswith(str(sandbox.resolve()))


class TestToolsHonourTheBoundary:
    @pytest.mark.parametrize(
        "call",
        [
            pytest.param(
                lambda wd: get_file_content(wd, "../outside/secret.txt"),
                id="get_file_content",
            ),
            pytest.param(lambda wd: get_files_info(wd, "../outside"), id="get_files_info"),
            pytest.param(lambda wd: search_files(wd, "SECRET", "../outside"), id="search_files"),
            pytest.param(
                lambda wd: edit_file(wd, "../outside/secret.txt", "SECRET", "x"),
                id="edit_file",
            ),
            pytest.param(
                lambda wd: run_python_file(wd, "../outside/script.py"), id="run_python_file"
            ),
        ],
    )
    def test_tool_refuses_to_reach_outside(self, sandbox, outside, call):
        # @log_errors turns the refusal into an "Error: ..." string for the model
        # rather than letting the exception escape.
        assert REFUSAL in call(str(sandbox))

    def test_write_file_refuses_and_leaves_no_trace(self, sandbox, outside):
        assert REFUSAL in write_file(str(sandbox), "../outside/pwned.txt", "payload")
        assert not (outside / "pwned.txt").exists()
