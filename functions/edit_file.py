import os

from google.genai import types

from functions.helpers import log_errors, validate_path


@log_errors
def edit_file(working_directory: str, file_path: str, old_string: str, new_string: str) -> str:
    """Replace a specific string in a file with a new string.

    This is the "surgical edit" tool — instead of rewriting the whole file,
    it finds exactly one occurrence of old_string and replaces it.  This is
    how real coding agents make targeted changes without touching the rest
    of the file.  Errors if old_string is not found or appears more than once.
    """
    """Replace a specific string in a file with a new string.

    This is the "surgical edit" tool — instead of rewriting the whole file,
    it finds exactly one occurrence of old_string and replaces it.  This is
    how real coding agents make targeted changes without touching the rest
    of the file.  Errors if old_string is not found or appears more than once.
    """
    target_path = validate_path(working_directory, file_path)
    if not os.path.isfile(target_path):
        raise Exception(f'"{file_path}" does not exist or is not a regular file')
    with open(target_path) as f:
        content = f.read()
    count = content.count(old_string)
    if count == 0:
        raise Exception(f"old_string not found in {file_path}")
    if count > 1:
        raise Exception(
            f"old_string appears {count} times in {file_path} — must be unique"
        )
    new_content = content.replace(old_string, new_string, 1)
    with open(target_path, "w") as f:
        f.write(new_content)
    return f"Successfully edited {file_path}"


schema_edit_file = types.FunctionDeclaration(
    name="edit_file",
    description=(
        "Makes a targeted edit to a file by replacing old_string with new_string. "
        "The old_string must appear exactly once in the file. "
        "Prefer this over write_file for small changes to existing files."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path of the file to edit",
            ),
            "old_string": types.Schema(
                type=types.Type.STRING,
                description="The exact string to find and replace (must appear once)",
            ),
            "new_string": types.Schema(
                type=types.Type.STRING,
                description="The replacement string",
            ),
        },
        required=["file_path", "old_string", "new_string"],
    ),
)
