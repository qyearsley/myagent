"""Gemini API setup and helpers.

Isolates Gemini-specific configuration (client, model, tool registration)
from the generic agentic loop in main.py.

API docs: https://googleapis.github.io/python-genai/genai.html#module-genai.types
"""

import os

from dotenv import load_dotenv
from google import genai
from google.genai.types import GenerateContentConfig, GenerateContentResponse, Tool

import prompts
from call_function import list_functions

DEFAULT_MODEL = "gemini-2.5-flash"


def create_client() -> genai.Client:
    """Initialize the Gemini client, loading the API key from environment variables."""
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not found in environment")
    return genai.Client(api_key=api_key)


def make_config() -> GenerateContentConfig:
    """Build the model config: register tool schemas and set the system prompt."""
    available_functions = Tool(function_declarations=list_functions())
    return GenerateContentConfig(
        tools=[available_functions],
        system_instruction=prompts.system_prompt,
    )


def print_metadata(response: GenerateContentResponse) -> None:
    """Print token usage from an API response (verbose mode only)."""
    metadata = response.usage_metadata
    if not metadata:
        return
    print(f"  Prompt tokens: {metadata.prompt_token_count}")
    print(f"  Response tokens: {metadata.candidates_token_count}")
