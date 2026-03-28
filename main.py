#!/usr/bin/env python3
"""
A minimal AI agent built on the Google Gemini API.

Key Gemini API concepts used throughout this file:
-----------------------------------------------------

  Content
      A single message in the conversation. Every Content has:
        - role: "user", "model", "tool"
        - parts: a list of Part objects (see below)
      Think of Content as one chat bubble.

  Part
      One atomic piece within a Content message. A Part can be:
        - Plain text        (Part.text)
        - A function call   (Part.function_call) — a request to run a tool
        - A function response (Part.function_response) — a tool result
      A single Content can hold multiple Parts, e.g. the model might return
      text *and* a function call in the same message.

  GenerateContentResponse (returned by client.models.generate_content)
      The full API response. Important fields:
        - candidates:      list of Candidate objects (usually just one).
                           Each Candidate wraps a Content with the model's
                           reply, so candidate.content is a Content.
        - usage_metadata:  token counts (prompt + response)
        - .text:           shortcut for the first candidate's text
        - .function_calls: list of FunctionCall Parts across candidates

  "messages" (the conversation history)
      Just a plain Python list[Content]. We pass it as `contents=` to
      generate_content each turn so the model sees the full conversation.
"""

import argparse
import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai.types import (
    Content,
    FunctionCall,
    GenerateContentConfig,
    GenerateContentResponse,
    Part,
    Tool,
)

import prompts
from config import MAX_ITERATIONS

from call_function import list_functions, call_function


MODEL_NAME = "gemini-2.5-flash"


def main() -> None:
    args = parse_args()
    api_key = load_api_key()
    client = genai.Client(api_key=api_key)
    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
    config: GenerateContentConfig = make_config()

    # The conversation history. Each entry is a Content (one message).
    # We seed it with the user's initial prompt.
    messages: list[Content] = [
        Content(role="user", parts=[Part(text=args.user_prompt)])
    ]

    for _ in range(MAX_ITERATIONS):
        if args.verbose:
            print(f"Starting agentic loop with {len(messages)} messages")
        # Send the full conversation so far; the model replies with a Response.
        response = client.models.generate_content(
            model=MODEL_NAME, contents=messages, config=config
        )
        if not response:
            raise RuntimeError("generate_content returned no response")
        if args.verbose:
            print_metadata(response)
        if not response.candidates:
            raise Exception("No response candidates")

        # Add candidates to the message list so that the agent keeps track of
        # conversation history.
        for candidate in response.candidates:
            if candidate.content:
                messages.append(candidate.content)

        # The model can either respond with plain text OR request function calls.
        # When it returns function_calls, it's asking the agent to execute tools
        # on its behalf -- this is the core of the "agentic" pattern.
        if response.function_calls:
            results: list[Part] = get_function_call_results(
                response.function_calls, verbose=args.verbose
            )
            # Append function results to messages.
            messages.append(Content(role="user", parts=results))
        elif response.text:
            print(response.text)
        if not response.function_calls:
            sys.exit(0)

    # If we got to this point we never exited with a final message above.
    print("No final message reached")
    sys.exit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    return parser.parse_args()


def load_api_key() -> str:
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("no api key found")
    return api_key


def make_config() -> GenerateContentConfig:
    # Register our tool schemas with the model so it knows what functions it
    # can call and what arguments they accept (see each schema_* declaration).
    # Optionally we can specify a temperature argument with a value between 0 and 1
    available_functions = Tool(function_declarations=list_functions())
    return GenerateContentConfig(
        tools=[available_functions],
        system_instruction=prompts.system_prompt,
    )


def print_metadata(response: GenerateContentResponse) -> None:
    metadata = response.usage_metadata
    if not metadata:
        print("No response metadata")
        sys.exit(1)
    prompt_tokens = metadata.prompt_token_count
    response_tokens = metadata.candidates_token_count
    print(f"Prompt tokens: {prompt_tokens}")
    print(f"Response tokens: {response_tokens}")


def get_function_call_results(
    function_calls: list[FunctionCall], verbose: bool = False
) -> list[Part]:
    """Execute each function the model requested and collect the results.

    Returns a list of Part objects (each wrapping a function_response) that
    should be sent back to the model in the next turn so it can see what
    the tools returned.
    """
    results: list[Part] = []
    for fc in function_calls:
        if verbose:
            print(f"Calling function: {fc.name}({fc.args})")
        # call_function returns a Content with role="tool" containing one Part.
        function_call_result: Content = call_function(fc, verbose=verbose)
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
            print(f"-> {fr.response}")
    return results


if __name__ == "__main__":
    main()
