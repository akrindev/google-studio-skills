#!/usr/bin/env python3
"""Retrieve batch job results.

Usage:
    python get_results.py <job_name>
    python get_results.py batches/abc123 --output results.jsonl

Requirements:
    pip install google-genai
"""

import argparse
import json
import os
import sys

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


def get_results(job_name: str, output: str | None = None) -> str | None:
    """Retrieve batch job results.

    Args:
        job_name: The batch job name/ID
        output: Optional output file path

    Returns:
        Results content or None
    """
    client = get_client()

    batch_job = client.batches.get(name=job_name)
    state = (
        batch_job.state.name
        if hasattr(batch_job.state, "name")
        else str(batch_job.state)
    )

    if state != "JOB_STATE_SUCCEEDED":
        print(f"Warning: Job is not completed. State: {state}")
        return None

    if (
        batch_job.dest
        and hasattr(batch_job.dest, "file_name")
        and batch_job.dest.file_name
    ):
        result_file_name = batch_job.dest.file_name
        print(f"Downloading results from: {result_file_name}")

        file_content = client.files.download(file=result_file_name)
        content = file_content.decode("utf-8")

        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Results saved to {output}")
        else:
            print("Results:")
            for line in content.strip().split("\n"):
                try:
                    result = json.loads(line)
                    print(f"  Key: {result.get('key', 'N/A')}")
                    if "response" in result:
                        text = result["response"].get("text", str(result["response"]))
                        print(f"  Response: {text[:200]}...")
                except json.JSONDecodeError:
                    print(f"  {line[:200]}...")

        return content

    elif batch_job.dest and hasattr(batch_job.dest, "inlined_responses"):
        print("Inline Results:")
        for i, resp in enumerate(batch_job.dest.inlined_responses):
            print(f"\nResponse {i + 1}:")
            if hasattr(resp, "response") and resp.response:
                try:
                    print(resp.response.text)
                except AttributeError:
                    print(str(resp.response))
            elif hasattr(resp, "error") and resp.error:
                print(f"Error: {resp.error}")
    else:
        print("No results found.")
        return None


def main():
    parser = argparse.ArgumentParser(description="Retrieve batch job results")
    parser.add_argument("job_name", help="Batch job name/ID")
    parser.add_argument("--output", "-o", help="Output file path for results")

    args = parser.parse_args()

    try:
        get_results(job_name=args.job_name, output=args.output)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
