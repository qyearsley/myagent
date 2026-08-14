# NOTE: Each tool function validates that file paths stay within the sandbox
# working directory using os.path.commonpath. This prevents the model from
# accessing files outside the permitted area via path traversal (e.g. "../../")
# or via a symlink inside the working directory that points outside it.

import functools
import os
import subprocess


def log_errors(func):
    """Decorator that catches exceptions in tool functions and prints them
    instead of crashing, so the agent can report the error to the model."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return f"Error: {e}"

    return wrapper


def validate_path(working_directory, path, action="access"):
    """Resolve path relative to working_directory and verify it stays inside.

    Returns the resolved absolute path, or raises if it escapes the sandbox.
    `action` is the verb used in the error message, so each tool can phrase the
    rejection in its own terms ("Cannot list", "Cannot write to", ...).

    Both sides are resolved with realpath so that symlinks are followed before
    the comparison. Using abspath/normpath here would let a symlink inside the
    working directory point outside it and slip past the check -- normpath is
    pure string manipulation and knows nothing about links. realpath also
    resolves paths that don't exist yet, which write_file relies on.
    """
    working_dir_abs = os.path.realpath(working_directory)
    target_path = os.path.realpath(os.path.join(working_dir_abs, path))
    if os.path.commonpath([working_dir_abs, target_path]) != working_dir_abs:
        raise Exception(
            f'Cannot {action} "{path}" as it is outside the permitted working directory'
        )
    return target_path


def run_subprocess(command, cwd, timeout=30, shell=False):
    """Run a command and return formatted output (stdout, stderr, exit code).

    Shared by run_python_file and run_bash_command — both need the same
    subprocess invocation and output formatting logic.
    """
    try:
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            cwd=os.path.abspath(cwd),
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return f"Error: command timed out after {timeout} seconds"
    output = ""
    if result.returncode != 0:
        output += f"Process exited with code {result.returncode}\n"
    if result.stdout:
        output += "STDOUT:\n" + result.stdout
    if result.stderr:
        output += "STDERR:\n" + result.stderr
    if not output:
        output = "No output produced."
    return output
