import os

from google.genai import types

from functions.helpers import log_errors, validate_path, run_subprocess


@log_errors
def run_python_file(working_directory: str, file_path: str, args: list[str] | None = None) -> str:
    """Runs a Python script within the working directory.

    Args:
        working_directory: The agent's current working directory.
        file_path: The path to the Python script to run, relative to the working directory.
        args: Optional list of arguments to pass to the Python script.

    Returns:
        The output from the script (stdout, stderr, and exit code if non-zero).

    Raises:
        Exception: If the file is not found, not a regular file, or not a Python file.
    """
    target_path = validate_path(working_directory, file_path)
    if not os.path.isfile(target_path):
        raise Exception(f'"{file_path}" does not exist or is not a regular file')
    if not target_path.endswith(".py"):
        raise Exception(f'"{file_path}" is not a Python file')
    command = ["python3", target_path]
    if args:
        command.extend(args)
    return run_subprocess(command, cwd=working_directory)


schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs a Python script, printing stdout and stderr if there is any, and ret code if non-zero",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path of Python script file to run",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description="Optional list of args to pass to the Python script, defaults to empty",
            ),
        },
        required=["file_path"],
    ),
)
