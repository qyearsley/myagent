#!/usr/bin/env python3

import argparse
import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

import prompts

from call_function import list_functions, call_function


def main():
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("no api key found")
    client = genai.Client(api_key=api_key)

    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

    model_name = "gemini-2.5-flash"

    # Register our tool schemas with the model so it knows what functions it
    # can call and what arguments they accept (see each schema_* declaration).
    available_functions = types.Tool(function_declarations=list_functions())
    config = types.GenerateContentConfig(
        tools=[available_functions],
        system_instruction=prompts.system_prompt,
        temperature=0.5,
    )

    response = client.models.generate_content(
        model=model_name, contents=messages, config=config
    )

    metadata = response.usage_metadata
    if not metadata:
        print("No reponse metadata")
        sys.exit(1)
    prompt_tokens = metadata.prompt_token_count
    response_tokens = metadata.candidates_token_count
    if args.verbose:
        print(f"Prompt tokens: {prompt_tokens}")
        print(f"Response tokens: {response_tokens}")
    if not response:
        raise RuntimeError("generate_content no response")

    # The model can either respond with plain text OR request function calls.
    # When it returns function_calls, it's asking the agent to execute tools
    # on its behalf -- this is the core of the "agentic" pattern.
    if response.function_calls:
        results = []
        for fc in response.function_calls:
            #print(f"Calling function: {fc.name}({fc.args})")
            function_call_result = call_function(fc, verbose=args.verbose)
            if not function_call_result.parts:
                raise Exception("Function call result has no parts")
            fr = function_call_result.parts[0].function_response
            if fr is None:
                raise Exception("Function response is None")
            if fr.response is None:
                raise Exception("Function response has no response")
            results.append(function_call_result.parts[0])
            if args.verbose:
                print(f"-> {fr.response}")
    else:
        print(response.text)


if __name__ == "__main__":
    main()
