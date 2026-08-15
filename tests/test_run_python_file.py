"""Tests for running Python scripts inside the sandbox.

Sandbox escape is covered in test_sandbox.py; these cover the happy path,
the argument passthrough, and how the tool reports a script that misbehaves.
"""

from functions.run_python_file import run_python_file


class TestRunPythonFile:
    def test_runs_a_script_and_returns_its_stdout(self, sandbox):
        assert run_python_file(str(sandbox), "main.py") == "STDOUT:\nhello\n"

    def test_runs_a_script_in_a_subdirectory(self, sandbox):
        (sandbox / "pkg" / "hi.py").write_text("print('from pkg')\n")
        assert "from pkg" in run_python_file(str(sandbox), "pkg/hi.py")

    def test_passes_arguments_through_to_the_script(self, sandbox):
        (sandbox / "echo.py").write_text("import sys\nprint(' '.join(sys.argv[1:]))\n")
        result = run_python_file(str(sandbox), "echo.py", ["3 + 5", "extra"])
        assert "3 + 5 extra" in result

    def test_reports_the_exit_code_when_the_script_fails(self, sandbox):
        (sandbox / "boom.py").write_text("raise SystemExit(3)\n")
        assert "Process exited with code 3" in run_python_file(str(sandbox), "boom.py")

    def test_reports_stderr(self, sandbox):
        (sandbox / "noisy.py").write_text("import sys\nsys.stderr.write('trouble\\n')\n")
        assert "STDERR:\ntrouble" in run_python_file(str(sandbox), "noisy.py")

    def test_says_so_when_the_script_prints_nothing(self, sandbox):
        (sandbox / "quiet.py").write_text("pass\n")
        assert run_python_file(str(sandbox), "quiet.py") == "No output produced."

    def test_refuses_a_file_that_does_not_exist(self, sandbox):
        result = run_python_file(str(sandbox), "nonexistent.py")
        assert "does not exist or is not a regular file" in result

    def test_refuses_a_directory(self, sandbox):
        assert "does not exist or is not a regular file" in run_python_file(str(sandbox), "pkg")

    def test_refuses_a_file_that_is_not_python(self, sandbox):
        (sandbox / "lorem.txt").write_text("not a script\n")
        assert "is not a Python file" in run_python_file(str(sandbox), "lorem.txt")
