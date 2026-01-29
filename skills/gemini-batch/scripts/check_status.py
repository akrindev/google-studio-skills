#!/usr/bin/env python3
"""Check batch job status.

Usage:
    python check_status.py <job_name>
    python check_status.py batches/abc123 --wait

Requirements:
    pip install google-genai
"""

import argparse
import os
import sys
import time

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


def check_status(job_name: str, wait: bool = False) -> str:
    """Check batch job status.

    Args:
        job_name: The batch job name/ID
        wait: Whether to poll until completion

    Returns:
        Final job state
    """
    client = get_client()

    completed_states = {
        "JOB_STATE_SUCCEEDED",
        "JOB_STATE_FAILED",
        "JOB_STATE_CANCELLED",
        "JOB_STATE_EXPIRED",
    }

    batch_job = client.batches.get(name=job_name)
    state = (
        batch_job.state.name
        if hasattr(batch_job.state, "name")
        else str(batch_job.state)
    )

    if wait:
        print(f"Polling status for job: {job_name}")
        while state not in completed_states:
            print(f"Current state: {state}")
            time.sleep(30)
            batch_job = client.batches.get(name=job_name)
            state = (
                batch_job.state.name
                if hasattr(batch_job.state, "name")
                else str(batch_job.state)
            )

    if state == "JOB_STATE_SUCCEEDED":
        print("Job succeeded!")
    elif state == "JOB_STATE_FAILED":
        print("Job failed!")
        if hasattr(batch_job, "error") and batch_job.error:
            print(f"Error: {batch_job.error}")
    else:
        print(f"Job state: {state}")

    return state


def main():
    parser = argparse.ArgumentParser(description="Check batch job status")
    parser.add_argument("job_name", help="Batch job name/ID")
    parser.add_argument(
        "--wait",
        "-w",
        action="store_true",
        help="Wait for job to complete (polls every 30s)",
    )

    args = parser.parse_args()

    try:
        check_status(job_name=args.job_name, wait=args.wait)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
