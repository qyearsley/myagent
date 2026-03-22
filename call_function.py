from functions.get_file_content import schema_get_file_content, get_file_content
from functions.get_files_info import schema_get_files_info, get_files_info
from functions.run_python_file import schema_run_python_file, run_python_file
from functions.write_file import schema_write_file, write_file

from google.genai import types

def call_function(function_call, verbose=False):
    """Dispatch a model-requested function call to the actual Python implementation.

    This is the bridge between the LLM and real code execution. The model
    returns a function name + arguments; we look up the matching Python
    function and invoke it, then wrap the result back into a format the
    model can consume in the next turn.
    """
    mapping = function_map()
    function_name = function_call.name or ""
    if function_name not in mapping:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )
    if verbose:
        print(f"Calling function: {function_call.name}({function_call.args})")
    else:
        print(f" - Calling function: {function_call.name}")

    args = dict(function_call.args) if function_call.args else {}
    # Sandbox: every tool operates within a fixed working directory so the
    # model can't access files outside the permitted area.
    args["working_directory"] = "./calculator"

    function_result = mapping[function_name](**args)

    # Return the result as a "tool" role message -- this is the Gemini API's
    # format for feeding function outputs back into the conversation.
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )


def function_map():
    """Maps function names (as the model knows them) to Python callables."""
    return {
        "get_file_content": get_file_content,
        "get_files_info": get_files_info,
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
        schema_run_python_file,
        schema_write_file,
    ]
