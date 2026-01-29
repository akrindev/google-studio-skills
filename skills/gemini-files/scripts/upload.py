#!/usr/bin/env python3
"""Upload files to Gemini File API.

Usage:
    python upload.py image.jpg
    python upload.py document.pdf --name "my-document"
    python upload.py video.mp4 --wait

Requirements:
    pip install google-genai
"""

import argparse
import os
import sys
import time
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


MIME_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".avi": "video/x-msvideo",
    ".webm": "video/webm",
    ".jsonl": "application/jsonl",
}


def upload_file(
    path: str,
    display_name: str | None = None,
    wait: bool = False,
) -> dict:
    """Upload a file to Gemini File API.

    Args:
        path: Path to the file
        display_name: Optional display name
        wait: Wait for processing to complete

    Returns:
        File info dict
    """
    from google.genai import types

    client = get_client()

    file_path = Path(path)
    if not file_path.exists():
        print(f"Error: File not found: {path}")
        sys.exit(1)

    mime_type = MIME_TYPES.get(file_path.suffix.lower(), "application/octet-stream")

    print(f"Uploading {path}...")

    uploaded_file = client.files.upload(
        file=path,
        config=types.UploadFileConfig(
            mime_type=mime_type,
            display_name=display_name or file_path.name,
        ),
    )

    print(f"Uploaded: {uploaded_file.name}")
    print(f"URI: {uploaded_file.uri}")
    print(f"State: {uploaded_file.state}")

    if wait and uploaded_file.state != "ACTIVE":
        print("Waiting for processing...")
        while True:
            file_info = client.files.get(name=uploaded_file.name)
            if file_info.state == "ACTIVE":
                print("File ready!")
                break
            elif file_info.state == "FAILED":
                print("Processing failed!")
                sys.exit(1)
            time.sleep(2)
            print("  Still processing...")

    return {
        "name": uploaded_file.name,
        "uri": uploaded_file.uri,
        "display_name": uploaded_file.display_name,
        "mime_type": mime_type,
        "state": uploaded_file.state,
    }


def main():
    parser = argparse.ArgumentParser(description="Upload files to Gemini File API")
    parser.add_argument("path", help="Path to the file to upload")
    parser.add_argument("--name", "-n", help="Display name for the file")
    parser.add_argument(
        "--wait", "-w", action="store_true", help="Wait for processing to complete"
    )

    args = parser.parse_args()

    try:
        result = upload_file(
            path=args.path,
            display_name=args.name,
            wait=args.wait,
        )
        print(f"\nFile name: {result['name']}")
        print("Use this name to reference the file in API calls")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
