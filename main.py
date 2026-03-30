#!/usr/bin/env python3
"""
A minimal AI agent that demonstrates the agentic loop pattern.

The agent receives a user prompt, calls an LLM, and if the LLM requests
tool calls (read files, run code, etc.) it executes them and feeds results
back — looping until the LLM produces a final text response.

Gemini API types used here (Content, Part, FunctionCall) are documented at:
  https://googleapis.github.io/python-genai/genai.html#module-genai.types
"""

import argparse
import sys

from google.genai.types import Content, FunctionCall, Part

from config import MAX_ITERATIONS
from gemini import MODEL_NAME, create_client, make_config, print_metadata
from call_function import call_function


def main() -> None:
    args = parse_args()
    client = create_client()
    config = make_config()

    # The conversation history persists across turns so the model remembers
    # prior context.  In REPL mode this is what gives multi-turn memory.
    messages: list[Content] = []

    if args.user_prompt:
        # Single-shot mode: run one prompt and exit.
        messages.append(Content(role="user", parts=[Part(text=args.user_prompt)]))
        agent_loop(client, config, messages, args.verbose, args.yes)
    else:
        # REPL mode: interactive loop.  The user types prompts, the agent
        # responds, and conversation history carries across turns — just
        # like a real coding agent session.
        repl(client, config, messages, args.verbose, args.yes)


def repl(client, config, messages, verbose, auto_confirm):
    """Interactive read-eval-print loop.

    Each user input becomes a new turn in the same conversation. The shared
    messages list means the model can reference earlier context ("now edit
    the file you just read").  Exit with quit/exit, Ctrl-C, or Ctrl-D.
    """
    print("myagent REPL (type 'exit' to stop)")
    while True:
        try:
            user_input = input("> ").strip()
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            # Ctrl-C cancels current input, doesn't exit.
            print()
            continue
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            break
        messages.append(Content(role="user", parts=[Part(text=user_input)]))
        agent_loop(client, config, messages, verbose, auto_confirm)


def agent_loop(client, config, messages, verbose, auto_confirm):
    """Run the agentic loop for a single user prompt.

    Calls the model repeatedly until it produces a final text response
    (no more function calls) or hits the iteration limit.  Each iteration
    the model may request tool calls, which we execute and feed back.
    """
    for iteration in range(1, MAX_ITERATIONS + 1):
        if verbose:
            print(f"[Iteration {iteration}/{MAX_ITERATIONS}, {len(messages)} messages]")
        response = client.models.generate_content(
            model=MODEL_NAME, contents=messages, config=config
        )
        if not response:
            raise RuntimeError("generate_content returned no response")
        if verbose:
            print_metadata(response)
        if not response.candidates:
            raise Exception("No response candidates")

        # Add the model's reply to conversation history.
        for candidate in response.candidates:
            if candidate.content:
                messages.append(candidate.content)

        # The model can either respond with plain text OR request function
        # calls.  When it returns function_calls, we execute the tools and
        # feed results back for the next iteration.
        if response.function_calls:
            results: list[Part] = get_function_call_results(
                response.function_calls, verbose=verbose,
                auto_confirm=auto_confirm,
            )
            messages.append(Content(role="user", parts=results))
        else:
            # No function calls — the model is done.  Print its response.
            if response.text:
                print(response.text)
            return

    print("Max iterations reached")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument(
        "user_prompt", type=str, nargs="?", default=None,
        help="User prompt (omit to enter interactive REPL mode)",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation prompts")
    return parser.parse_args()


def get_function_call_results(
    function_calls: list[FunctionCall], verbose: bool = False,
    auto_confirm: bool = False,
) -> list[Part]:
    """Execute each function the model requested and collect the results.

    Returns a list of Part objects (each wrapping a function_response) that
    should be sent back to the model in the next turn so it can see what
    the tools returned.
    """
    results: list[Part] = []
    for fc in function_calls:
        # call_function returns a Content with role="tool" containing one Part.
        function_call_result: Content = call_function(
            fc, verbose=verbose, auto_confirm=auto_confirm,
        )
        if not function_call_result.parts:
            raise Exception("Function call result has no parts")
        fr = function_call_result.parts[0].function_response
        if fr is None:
            raise Exception("Function response is None")
        if fr.response is None:
            raise Exception("Function response has no response")
        # We extract just the Part (not the whole Content) because we'll
        # bundle all function-response Parts into a single Content message.
        results.append(function_call_result.parts[0])
        if verbose:
            # Show a truncated preview of the result so the user can see what
            # the model will receive, without flooding the terminal.
            result_str = str(fr.response.get("result", fr.response))
            if len(result_str) > 200:
                result_str = result_str[:200] + "..."
            print(f"    -> ({len(str(fr.response))} chars) {result_str}")
    return results


if __name__ == "__main__":
    main()
