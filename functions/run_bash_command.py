import os
import subprocess

from google.genai import types

from functions.helpers import log_errors


@log_errors
def run_bash_command(working_directory, command):
    """Run a shell command in the working directory and return its output."""
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        cwd=os.path.abspath(working_directory),
        text=True,
        timeout=30,
    )
    output = ""
    if result.returncode != 0:
        output += f"Process exited with code {result.returncode}\n"
    if result.stdout:
        output += "STDOUT:\n" + result.stdout
    if result.stderr:
        output += "STDERR:\n" + result.stderr
    if not output:
        output = "No output produced."
    return output


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
