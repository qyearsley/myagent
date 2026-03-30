# NOTE: Each tool function validates that file paths stay within the sandbox
# working directory using os.path.commonpath. This prevents the model from
# accessing files outside the permitted area via path traversal (e.g. "../../").

import os
import subprocess


def log_errors(func):
    """Decorator that catches exceptions in tool functions and prints them
    instead of crashing, so the agent can report the error to the model."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return f"Error: {e}"

    return wrapper


def validate_path(working_directory, path):
    """Resolve path relative to working_directory and verify it stays inside.
    Returns the resolved absolute path, or raises if it escapes the sandbox."""
    working_dir_abs = os.path.abspath(working_directory)
    target_path = os.path.normpath(os.path.join(working_dir_abs, path))
    if os.path.commonpath([working_dir_abs, target_path]) != working_dir_abs:
        raise Exception(
            f'Cannot access "{path}" as it is outside the permitted working directory'
        )
    return target_path


def run_subprocess(command, cwd, timeout=30, shell=False):
    """Run a command and return formatted output (stdout, stderr, exit code).

    Shared by run_python_file and run_bash_command — both need the same
    subprocess invocation and output formatting logic.
    """
    result = subprocess.run(
        command, shell=shell, capture_output=True,
        cwd=os.path.abspath(cwd), text=True, timeout=timeout,
    )
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
