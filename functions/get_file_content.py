import os

from config import MAX_CHARS


def log_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f'  Error: {e}')
    return wrapper


@log_errors
def get_file_content(working_directory, file_path):
    working_dir_abs = os.path.abspath(working_directory)
    target_path = os.path.normpath(os.path.join(working_dir_abs, file_path))
    valid_target_path = (
        os.path.commonpath([working_dir_abs, target_path]) == working_dir_abs
    )
    if not valid_target_path:
        raise Exception(f'Cannot read "{file_path}" as it is outside the permitted working directory')
    if not os.path.isfile(target_path):
        raise Exception(f'File not found or is not a regular file: "{file_path}"')
    fd = open(target_path)
    content = fd.read(MAX_CHARS)
    if fd.read(1):
        content += f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
    print(content)
