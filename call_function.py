import os

from google.genai.types import Content, Part

from config import WORKING_DIRECTORY
from functions.edit_file import schema_edit_file, edit_file
from functions.get_file_content import schema_get_file_content, get_file_content
from functions.get_files_info import schema_get_files_info, get_files_info
from functions.run_bash_command import schema_run_bash_command, run_bash_command
from functions.run_python_file import schema_run_python_file, run_python_file
from functions.write_file import schema_write_file, write_file


def describe_call(name, args):
    """Return a short, human-readable summary of a tool call.

    Real agents always show the user what they're doing — not the raw
    function signature, but a concise description like "Reading main.py".
    Each tool has a different "interesting" argument to surface.
    """
    match name:
        case "get_file_content":
            return f"Reading {args.get('file_path', '?')}"
        case "get_files_info":
            directory = args.get("directory", ".")
            abs_path = os.path.abspath(os.path.join(WORKING_DIRECTORY, directory))
            return f"Listing files in {abs_path}"
        case "write_file":
            content = args.get("content", "")
            return f"Writing {args.get('file_path', '?')} ({len(content)} chars)"
        case "edit_file":
            return f"Editing {args.get('file_path', '?')}"
        case "run_python_file":
            parts = [f"Running {args.get('file_path', '?')}"]
            if args.get("args"):
                parts.append(f"with args {args['args']}")
            return " ".join(parts)
        case "run_bash_command":
            return f"Running: {args.get('command', '?')}"
        case _:
            return f"Calling {name}"


def confirm(description):
    """Prompt the user to approve a mutating action. Default is yes."""
    answer = input(f"  Allow '{description}'? [Y/n] ").strip().lower()
    return answer in ("", "y", "yes")


# Tools that modify state require user confirmation before running.
# Read-only tools (get_file_content, get_files_info) run without asking.
NEEDS_CONFIRMATION = {"write_file", "edit_file", "run_python_file", "run_bash_command"}


def call_function(function_call, verbose=False, auto_confirm=False):
    """Dispatch a model-requested function call to the actual Python implementation.

    This is the bridge between the LLM and real code execution. The model
    returns a function name + arguments; we look up the matching Python
    function and invoke it, then wrap the result back into a format the
    model can consume in the next turn.
    """
    mapping = function_map()
    function_name = function_call.name or ""
    if function_name not in mapping:
        return Content(
            role="tool",
            parts=[
                Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )
    args = dict(function_call.args) if function_call.args else {}
    description = describe_call(function_name, args)
    # Always print a human-readable summary of what the tool is doing.
    print(f"  {description}")

    # Ask for confirmation before mutating actions.
    if function_name in NEEDS_CONFIRMATION and not auto_confirm:
        if not confirm(description):
            return Content(
                role="tool",
                parts=[
                    Part.from_function_response(
                        name=function_name,
                        response={"result": "User denied this action."},
                    )
                ],
            )

    # Sandbox: every tool operates within a fixed working directory so the
    # model can't access files outside the permitted area.
    args["working_directory"] = WORKING_DIRECTORY

    function_result = mapping[function_name](**args)

    # Return the result as a "tool" role message -- this is the Gemini API's
    # format for feeding function outputs back into the conversation.
    return Content(
        role="tool",
        parts=[
            Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )


def function_map():
    """Maps function names (as the model knows them) to Python callables."""
    return {
        "edit_file": edit_file,
        "get_file_content": get_file_content,
        "get_files_info": get_files_info,
        "run_bash_command": run_bash_command,
        "run_python_file": run_python_file,
        "write_file": write_file,
    }


def list_functions():
    """Return the schema declarations that tell the model what tools exist.

    Each schema describes a function's name, description, and parameter types
    so the model can decide when and how to call it.
    """
    return [
        schema_get_files_info,
        schema_get_file_content,
        schema_edit_file,
        schema_run_bash_command,
        schema_run_python_file,
        schema_write_file,
    ]
