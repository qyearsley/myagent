import os

from google.genai import types

from functions.helpers import log_errors, validate_path


@log_errors
def get_files_info(working_directory, directory="."):
    target_dir = validate_path(working_directory, directory)
    output = "Result for current directory:\n"
    if not os.path.isdir(target_dir):
        raise Exception(f'"{directory}" is not a directory')
    for item in os.listdir(target_dir):
        path = os.path.join(target_dir, item)
        size = os.path.getsize(path)
        is_dir = os.path.isdir(path)
        output += f" - {item}: file_size={size} bytes, is_dir={is_dir}\n"

    return output


schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
            ),
        },
    ),
)
