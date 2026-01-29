---
name: gemini-text
description: Generate text content using Google Gemini models. Use for text generation, multimodal prompts with images, thinking mode for complex reasoning, JSON-formatted outputs, and Google Search grounding for real-time information. Triggers on "generate with gemini", "use gemini for text", "AI text generation", "multimodal prompt", "gemini thinking mode", "grounded response".
---

# Gemini Text Generation

Generate content using Google's Gemini API with advanced capabilities including system instructions, thinking mode, JSON output, and Google Search grounding.

## Prerequisites

- Set `GOOGLE_API_KEY` or `GEMINI_API_KEY` environment variable
- Install: `pip install google-genai`

## Quick Start

```python
from google import genai

client = genai.Client()
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Explain quantum computing in simple terms"
)
print(response.text)
```

## Available Scripts

- **scripts/generate.py** - Full-featured text generation with all options

## Features

### Basic Generation

```python
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Your prompt here"
)
```

### System Instructions

Define model persona or behavior:

```python
from google.genai import types

response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction="You are a helpful coding assistant."
    ),
    contents="How do I read a file in Python?"
)
```

### Thinking Mode

Enable extended reasoning for complex tasks:

```python
config = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(thinking_budget=1024)
)
# Use thinking_budget=0 to disable thinking
```

### JSON Output

Force structured JSON responses:

```python
config = types.GenerateContentConfig(
    response_mime_type="application/json"
)
```

### Google Search Grounding

Enable real-time web search for current information:

```python
grounding_tool = types.Tool(google_search=types.GoogleSearch())
config = types.GenerateContentConfig(tools=[grounding_tool])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Who won the latest Super Bowl?",
    config=config
)
# Response includes groundingMetadata with citations
```

### Multimodal (Image + Text)

```python
from pathlib import Path

image_bytes = Path("photo.png").read_bytes()
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Part(text="Describe this image"),
        types.Part(inline_data=types.Blob(
            mime_type="image/png",
            data=image_bytes
        ))
    ]
)
```

## Configuration Options

| Parameter | Type | Description |
|-----------|------|-------------|
| `temperature` | float | Controls randomness (0.0-2.0, default 1.0) |
| `top_p` | float | Nucleus sampling threshold (default 0.95) |
| `top_k` | int | Top-k sampling (default 64) |
| `max_output_tokens` | int | Maximum response length |
| `response_mime_type` | str | Force output format ("application/json") |

## Models

See [references/models.md](references/models.md) for detailed model information.

| Model | Best For | Context |
|-------|----------|---------|
| `gemini-3-flash-preview` | Fast, agentic, multimodal (default) | 1M tokens |
| `gemini-3-pro-preview` | Most intelligent, complex reasoning | 1M tokens |
| `gemini-2.5-flash` | Stable, general purpose | 1M tokens |
| `gemini-2.5-pro` | Complex reasoning, code, math, STEM | 1M tokens |

## Error Handling

```python
try:
    response = client.models.generate_content(...)
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
    # Check API key, model availability, quota
```
