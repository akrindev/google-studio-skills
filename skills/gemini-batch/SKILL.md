---
name: gemini-batch
description: Process large volumes of requests using Gemini Batch API. Use for batch processing, bulk text generation, processing JSONL files, async job execution, and cost-efficient high-volume AI tasks. Triggers on "batch processing", "bulk requests", "JSONL", "async job", "batch job".
---

# Gemini Batch Processing

Process large volumes of requests efficiently using the Gemini Batch API for cost savings and high throughput.

## Prerequisites

- Set `GOOGLE_API_KEY` or `GEMINI_API_KEY` environment variable
- Install: `pip install google-genai`

## Quick Start

```python
from google import genai
from google.genai import types

client = genai.Client()

# Upload JSONL file with requests
uploaded_file = client.files.upload(
    file="my-batch-requests.jsonl",
    config=types.UploadFileConfig(
        display_name="batch-input",
        mime_type="jsonl"
    )
)

# Create batch job
batch_job = client.batches.create(
    model="gemini-3-flash-preview",
    src=uploaded_file.name,
    config={"display_name": "my-batch-job"}
)

print(f"Job created: {batch_job.name}")
```

## Available Scripts

- **scripts/create_batch.py** - Create batch job from JSONL file
- **scripts/check_status.py** - Check batch job status
- **scripts/get_results.py** - Retrieve batch job results

## JSONL Input Format

Each line is a JSON object with a request:

```jsonl
{"key": "request-1", "request": {"contents": [{"parts": [{"text": "Describe photosynthesis"}]}]}}
{"key": "request-2", "request": {"contents": [{"parts": [{"text": "What is gravity?"}]}]}}
```

## Creating JSONL File

```python
import json

with open("batch-requests.jsonl", "w") as f:
    requests = [
        {"key": "req-1", "request": {"contents": [{"parts": [{"text": "Question 1"}]}]}},
        {"key": "req-2", "request": {"contents": [{"parts": [{"text": "Question 2"}]}]}},
    ]
    for req in requests:
        f.write(json.dumps(req) + "\n")
```

## Checking Job Status

```python
batch_job = client.batches.get(name=job_name)
print(f"State: {batch_job.state}")

# States: JOB_STATE_PENDING, JOB_STATE_RUNNING, 
#         JOB_STATE_SUCCEEDED, JOB_STATE_FAILED, JOB_STATE_CANCELLED
```

## Retrieving Results

```python
if batch_job.state == "JOB_STATE_SUCCEEDED":
    if batch_job.dest.file_name:
        content = client.files.download(file=batch_job.dest.file_name)
        results = content.decode("utf-8")
```

## Inline vs File-Based

| Method | Best For | Size Limit |
|--------|----------|------------|
| Inline requests | Small batches | <20MB total |
| File upload | Large batches | Unlimited |

## Supported Models

- `gemini-3-flash-preview` (recommended)
- `gemini-3-pro-preview`
- `gemini-2.5-flash`
- `gemini-2.5-pro`

## Cost Benefits

Batch API typically offers:
- Lower per-token pricing
- Higher throughput
- No rate limiting per request
