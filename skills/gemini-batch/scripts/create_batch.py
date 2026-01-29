#!/usr/bin/env python3
"""Create a batch job from a JSONL file.

Usage:
    python create_batch.py requests.jsonl
    python create_batch.py requests.jsonl --model gemini-3-flash-preview
    python create_batch.py requests.jsonl --name "my-batch-job"

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


def create_batch_job(
    input_file: str,
    model: str = "gemini-3-flash-preview",
    display_name: str | None = None,
) -> str:
    """Create a batch job from a JSONL file.

    Args:
        input_file: Path to JSONL file with requests
        model: Model ID to use
        display_name: Optional display name for the job

    Returns:
        Job name/ID
    """
    from google.genai import types

    client = get_client()

    file_path = Path(input_file)
    if not file_path.exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    print(f"Uploading batch input file: {input_file}...")

    uploaded_file = client.files.upload(
        file=input_file,
        config=types.UploadFileConfig(
            display_name=display_name or file_path.stem, mime_type="jsonl"
        ),
    )

    print(f"File uploaded: {uploaded_file.name}")

    batch_job = client.batches.create(
        model=model,
        src=uploaded_file.name,
        config={
            "display_name": display_name or f"batch-{file_path.stem}",
        },
    )

    print(f"Batch job created: {batch_job.name}")
    return batch_job.name


def main():
    parser = argparse.ArgumentParser(description="Create a batch job from a JSONL file")
    parser.add_argument("input_file", help="Path to JSONL file with requests")
    parser.add_argument(
        "--model",
        "-m",
        default="gemini-3-flash-preview",
        help="Model ID (default: gemini-3-flash-preview)",
    )
    parser.add_argument("--name", "-n", help="Display name for the batch job")

    args = parser.parse_args()

    try:
        job_name = create_batch_job(
            input_file=args.input_file,
            model=args.model,
            display_name=args.name,
        )
        print(f"\nJob name: {job_name}")
        print("Use check_status.py to monitor progress")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
