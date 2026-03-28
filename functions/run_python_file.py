import os
import subprocess

from google.genai import types

from functions.helpers import log_errors, validate_path


@log_errors
def run_python_file(working_directory, file_path, args=None):
    target_path = validate_path(working_directory, file_path)
    if not os.path.isfile(target_path):
        raise Exception(f'"{file_path}" does not exist or is not a regular file')
    if not target_path.endswith(".py"):
        raise Exception(f'"{file_path}" is not a Python file')
    command = ["python", target_path]
    if args:
        command.extend(args)
    result = subprocess.run(
        command, capture_output=True, cwd=os.path.abspath(working_directory), text=True, timeout=30
    )
    output = ""
    if result.returncode != 0:
        output += f"Process exited with code {result.returncode}\n"
    if not result.stdout and not result.stderr:
        output += "No output produced.\n"
        return
    output += "STDOUT:\n" + result.stdout + "STDERR:\n" + result.stderr

    return output


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
