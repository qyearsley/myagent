import os

from google.genai import types

from config import MAX_CHARS
from functions.helpers import log_errors, validate_path


@log_errors
def get_file_content(working_directory, file_path):
    target_path = validate_path(working_directory, file_path)
    if not os.path.isfile(target_path):
        raise Exception(f'File not found or is not a regular file: "{file_path}"')
    with open(target_path) as f:
        output = f.read(MAX_CHARS)
        if f.read(1):
            output += f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'

    return output


schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Prints the content of a regular file, truncating if it is very large",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path to read, relative to the working directory",
            ),
        },
    ),
)
