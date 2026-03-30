from google.genai import types

from functions.helpers import log_errors, run_subprocess


@log_errors
def run_bash_command(working_directory, command):
    """Run a shell command in the working directory and return its output.

    NOTE: Unlike other tools, this doesn't use validate_path because it takes
    a command string, not a file path.  Sandboxing is limited to setting cwd —
    the command itself can still access files outside the working directory.
    This is inherently more dangerous than the file-based tools, which is why
    it requires user confirmation before running.
    """
    return run_subprocess(command, cwd=working_directory, shell=True)


schema_run_bash_command = types.FunctionDeclaration(
    name="run_bash_command",
    description="Runs a bash command in the working directory, returning stdout and stderr",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "command": types.Schema(
                type=types.Type.STRING,
                description="The bash command to run",
            ),
        },
        required=["command"],
    ),
)
