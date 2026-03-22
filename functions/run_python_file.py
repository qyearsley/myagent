import os
import subprocess

from google.genai import types


def log_errors_python(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"  Error: running Python file: {e}")

    return wrapper


@log_errors_python
def run_python_file(working_directory, file_path, args=None):
    working_dir_abs = os.path.abspath(working_directory)
    target_path = os.path.normpath(os.path.join(working_dir_abs, file_path))
    valid_target_path = (
        os.path.commonpath([working_dir_abs, target_path]) == working_dir_abs
    )
    if not valid_target_path:
        raise Exception(
            f'Cannot execute "{file_path}" as it is outside the permitted working directory'
        )
    if not os.path.isfile(target_path):
        raise Exception(f'"{file_path}" does not exist or is not a regular file')
    if not target_path.endswith(".py"):
        raise Exception(f'"{file_path}" is not a Python file')
    command = ["python", target_path]
    if args:
        command.extend(args)
    result = subprocess.run(
        command, capture_output=True, cwd=working_dir_abs, text=True, timeout=30
    )
    if result.returncode != 0:
        print(f"Process exited with code {result.returncode}")
    if not result.stdout and not result.stderr:
        print("No output produced.")
        return
    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)


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
                description="Optional arg, list of args to pass to the Python script",
            ),
        },
    ),
)
