# myagent

A minimal AI coding agent that demonstrates the **agentic loop** pattern: the LLM can call tools (read files, edit code, run commands), see the results, and iterate until the task is done.

Built with Python and the Gemini API. Intended as a learning project — small enough to read end-to-end, complete enough to actually use.

## How It Works

```
User prompt
    ↓
┌─→ LLM generates response
│       ├─ Text only → print and done
│       └─ Tool calls → execute tools, feed results back
└───────────────────────────────────────────────────────┘
```

The loop runs until the model produces a final text response or hits the iteration limit (20).

## Tools

| Tool               | Description                              |
| ------------------ | ---------------------------------------- |
| `get_files_info`   | List files in a directory                |
| `get_file_content` | Read a file                              |
| `search_files`     | Search for text across files (grep-like) |
| `edit_file`        | Replace a specific string in a file      |
| `write_file`       | Create or overwrite a file               |
| `run_python_file`  | Execute a Python script                  |
| `run_bash_command` | Run a shell command                      |

Mutating tools (edit, write, run) require confirmation unless `--yes` is passed. All file tools are sandboxed to the working directory.

## Setup

Requires Python 3.13+ and a [Gemini API key](https://aistudio.google.com/apikey).

```bash
uv sync                          # install dependencies
echo "GEMINI_API_KEY=..." > .env # add your API key
```

## Usage

```bash
python3 main.py                            # interactive REPL
python3 main.py "find and fix the bug"     # single-shot
python3 main.py -d ./myproject "run tests" # point at a directory
python3 main.py -m gemini-2.5-pro "..."    # use a different model
python3 main.py --verbose --yes "..."      # verbose + auto-confirm
```

## Project Structure

```
main.py           – Entry point and agentic loop
gemini.py         – Gemini API client setup
call_function.py  – Tool dispatch and confirmation flow
prompts.py        – System prompt
config.py         – Defaults (max iterations, max file chars)
functions/        – Tool implementations
  helpers.py      – Path validation, subprocess runner, error handling
  search_files.py, get_file_content.py, edit_file.py, ...
calculator/       – Sample project the agent can work on
```
