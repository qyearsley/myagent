#!/usr/bin/env python3

import os
from dotenv import load_dotenv

from google import genai


def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("no api key found")
    client = genai.Client(api_key=api_key)
    contents = "Why is Boot.dev such a great place to learn backend development? Use one paragraph maximum."
    response = client.models.generate_content(model="gemini-2.5-flash", contents=contents)
    if not response:
        raise RuntimeError("generate_content no response")
    print(response.text)


if __name__ == "__main__":
    main()
