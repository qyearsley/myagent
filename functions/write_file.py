import os


def log_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f'  Error: {e}')
    return wrapper


@log_errors
def write_file(working_directory, file_path, content):
    working_dir_abs = os.path.abspath(working_directory)
    target_path = os.path.normpath(os.path.join(working_dir_abs, file_path))
    valid_target_path = (
        os.path.commonpath([working_dir_abs, target_path]) == working_dir_abs
    )
    if not valid_target_path:
        raise Exception(f'Cannot write to "{file_path}" as it is outside the permitted working directory')
    if (os.path.isdir(target_path)):
        raise Exception(f'Cannot write to "{file_path}" as it is a directory')
    # Make sure that all parent directories of the file_path exist.
    parent_dir = os.path.dirname(target_path)
    os.makedirs(parent_dir, exist_ok=True)
    fd = open(target_path, "w")
    fd.write(content)
    print(f'Successfully wrote to "{file_path}" ({len(content)} characters written)')
