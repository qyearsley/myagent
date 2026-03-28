import os

from google.genai import types

from functions.helpers import log_errors, validate_path


@log_errors
def write_file(working_directory, file_path, content):
    target_path = validate_path(working_directory, file_path)
    if os.path.isdir(target_path):
        raise Exception(f'Cannot write to "{file_path}" as it is a directory')
    # Make sure that all parent directories of the file_path exist.
    parent_dir = os.path.dirname(target_path)
    os.makedirs(parent_dir, exist_ok=True)
    with open(target_path, "w") as f:
        f.write(content)
    return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'


schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a file, creating parent directories if needed",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path of regular file to write",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="File content to write",
            ),
        },
    ),
)
