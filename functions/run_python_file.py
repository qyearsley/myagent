import os
import subprocess


def log_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f'  Error: running Python file: {e}')
    return wrapper


@log_errors
def run_python_file(working_directory, file_path, args=None):
    working_dir_abs = os.path.abspath(working_directory)
    target_path = os.path.normpath(os.path.join(working_dir_abs, file_path))
    valid_target_path = (
        os.path.commonpath([working_dir_abs, target_path]) == working_dir_abs
    )
    if not valid_target_path:
        raise Exception(f'Cannot execute "{file_path}" as it is outside the permitted working directory')
    if not os.path.isfile(target_path):
        raise Exception(f'"{file_path}" does not exist or is not a regular file')
    if not target_path.endswith('.py'):
        raise Exception(f'"{file_path}" is not a Python file')
    command = ["python", target_path]
    if args:
        command.extend(args)
    result = subprocess.run(command, capture_output=True, cwd=working_dir_abs, text=True, timeout=30)
    if result.returncode != 0:
        print(f'Process exited with code {result.returncode}')
    if not result.stdout and not result.stderr:
        print(f'No output produced.')
        return
    print('STDOUT:')
    print(result.stdout)
    print('STDERR:')
    print(result.stderr)
