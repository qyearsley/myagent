import os

from google.genai import types

from functions.helpers import log_errors, validate_path

# Directories that are almost never useful to search inside.
SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules", ".mypy_cache"}
MAX_RESULTS = 50


@log_errors
def search_files(working_directory: str, pattern: str, path: str = ".") -> str:
    """Search for a text pattern across files in the working directory.

    Walks the file tree, skipping binary files and common noise directories.
    Returns matching lines in file:line_number:content format, capped at
    MAX_RESULTS to avoid flooding the model's context.
    """
    """Search for a text pattern across files in the working directory.

    Walks the file tree, skipping binary files and common noise directories.
    Returns matching lines in file:line_number:content format, capped at
    MAX_RESULTS to avoid flooding the model's context.
    """
    search_dir = validate_path(working_directory, path)
    if not os.path.isdir(search_dir):
        raise Exception(f'"{path}" is not a directory')

    results = []
    for root, dirs, files in os.walk(search_dir):
        # Prune noisy directories in-place so os.walk skips them.
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for filename in sorted(files):
            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, os.path.abspath(working_directory))
            try:
                with open(filepath, "r") as f:
                    for line_num, line in enumerate(f, 1):
                        if pattern in line:
                            results.append(f"{rel_path}:{line_num}:{line.rstrip()}")
                            if len(results) >= MAX_RESULTS:
                                results.append(f"[...stopped at {MAX_RESULTS} matches]")
                                return "\n".join(results)
            except (UnicodeDecodeError, PermissionError):
                # Skip binary files and unreadable files.
                continue

    if not results:
        return f"No matches found for '{pattern}'"
    return "\n".join(results)


schema_search_files = types.FunctionDeclaration(
    name="search_files",
    description=(
        "Searches for a text pattern across all files in the working directory. "
        "Returns matching lines with file paths and line numbers. "
        "Use this to find where functions, variables, or strings are used."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "pattern": types.Schema(
                type=types.Type.STRING,
                description="Text pattern to search for (substring match)",
            ),
            "path": types.Schema(
                type=types.Type.STRING,
                description="Directory to search within, relative to working directory (default: root)",
            ),
        },
        required=["pattern"],
    ),
)
