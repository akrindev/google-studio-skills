#!/usr/bin/env python3
"""Generate text content using Gemini API.

Usage:
    python generate.py "Your prompt here"
    python generate.py "Describe this" --image photo.png
    python generate.py "Complex task" --thinking
    python generate.py "Return JSON" --json
    python generate.py "Current events" --grounding
    python generate.py "Be helpful" --system "You are a coding assistant"

Requirements:
    pip install google-genai
"""

import argparse
import os
import sys
from pathlib import Path

# Load .env file if present
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


def get_client():
    """Get Gemini API client."""
    try:
        from google import genai
    except ImportError:
        print("Error: google-genai not installed. Run: pip install google-genai")
        sys.exit(1)

    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable")
        sys.exit(1)

    return genai.Client(api_key=api_key)


def generate_content(
    prompt: str,
    model: str = "gemini-3-flash-preview",
    image_path: str | None = None,
    system_instruction: str | None = None,
    thinking: bool = False,
    json_output: bool = False,
    grounding: bool = False,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    """Generate content using Gemini with advanced settings.

    Args:
        prompt: The text prompt
        model: Model ID (default: gemini-3-flash-preview)
        image_path: Optional path to image for multimodal
        system_instruction: Optional system instruction
        thinking: Enable thinking mode
        json_output: Force JSON response format
        grounding: Enable Google Search grounding
        temperature: Sampling temperature (0.0-2.0)
        max_tokens: Maximum output tokens

    Returns:
        Generated text response
    """
    from google.genai import types

    client = get_client()

    # Build contents
    contents = []
    if image_path:
        path = Path(image_path)
        if not path.exists():
            print(f"Error: Image file not found: {image_path}")
            sys.exit(1)

        image_bytes = path.read_bytes()
        mime_type = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"

        contents = types.Content(
            parts=[
                types.Part(text=prompt),
                types.Part(
                    inline_data=types.Blob(mime_type=mime_type, data=image_bytes)
                ),
            ],
            role="user",
        )
    else:
        contents = prompt

    # Build config
    config = types.GenerateContentConfig()

    if system_instruction:
        config.system_instruction = system_instruction

    if thinking:
        config.thinking_config = types.ThinkingConfig(thinking_budget=1024)

    if json_output:
        config.response_mime_type = "application/json"

    if grounding:
        config.tools = [types.Tool(google_search=types.GoogleSearch())]

    if temperature is not None:
        config.temperature = temperature

    if max_tokens is not None:
        config.max_output_tokens = max_tokens

    # Generate
    response = client.models.generate_content(
        model=model, contents=contents, config=config
    )

    return response.text


def main():
    parser = argparse.ArgumentParser(
        description="Generate text content using Gemini API"
    )
    parser.add_argument("prompt", help="The text prompt")
    parser.add_argument(
        "--model",
        "-m",
        default="gemini-3-flash-preview",
        help="Model ID (default: gemini-3-flash-preview). Options: gemini-3-flash-preview, gemini-3-pro-preview, gemini-2.5-flash, gemini-2.5-pro",
    )
    parser.add_argument("--image", "-i", help="Path to image for multimodal prompt")
    parser.add_argument("--system", "-s", help="System instruction")
    parser.add_argument(
        "--thinking", "-t", action="store_true", help="Enable thinking mode"
    )
    parser.add_argument(
        "--json", "-j", action="store_true", help="Force JSON response format"
    )
    parser.add_argument(
        "--grounding", "-g", action="store_true", help="Enable Google Search grounding"
    )
    parser.add_argument(
        "--temperature", type=float, help="Sampling temperature (0.0-2.0)"
    )
    parser.add_argument("--max-tokens", type=int, help="Maximum output tokens")

    args = parser.parse_args()

    try:
        result = generate_content(
            prompt=args.prompt,
            model=args.model,
            image_path=args.image,
            system_instruction=args.system,
            thinking=args.thinking,
            json_output=args.json,
            grounding=args.grounding,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
        )
        print(result)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
