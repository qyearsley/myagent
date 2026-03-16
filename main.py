#!/usr/bin/env python3

import argparse
import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

import prompts


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

    model_name="gemini-2.5-flash"
    config = types.GenerateContentConfig(
        system_instruction=prompts.system_prompt,
        temperature=0)

    response = client.models.generate_content(
        model=model_name,
        contents=messages,
        config=config
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
    print(response.text)


if __name__ == "__main__":
    main()
