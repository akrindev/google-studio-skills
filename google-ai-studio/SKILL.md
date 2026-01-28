---
name: Google AI Studio (Gemini)
description: Interact with Google's Gemini models via Google AI Studio. features support for Gemini 3, Imagen 4, TTS, Embeddings, and multimodal generation.
---

# Google AI Studio (Gemini) Skill

This skill allows you to interact with Google's Gemini models using the Python SDK. You can generate content, list available models, upload files, generate images, convert text to speech, and create embeddings.

## Prerequisites

-   **Python 3.9+** must be installed.
-   **Dependencies**: Run `pip install -r requirements.txt` in this directory.
-   **API Key**: Set the `GOOGLE_API_KEY` environment variable.

## Usage

### Listing Models

See compatible models (including Gemini 3 variants):

```bash
python scripts/gemini_client.py list-models
```

### Generating Content (Gemini 3)

Generate text using the latest Gemini 3 models (e.g., `gemini-3.0-pro-001`, `gemini-3.0-flash-001`):

```bash
python scripts/gemini_client.py generate "Explain advanced physics" --model "gemini-3.0-flash-001"
```

To enable potential "thinking" or reasoning capabilities (if supported by model config):

```bash
python scripts/gemini_client.py generate "Solve this riddle" --model "gemini-3.0-pro-001" --thinking
```

### Image Generation (Imagen 4 & Nano Banana Pro)

Generate high-quality images:

```bash
python scripts/gemini_client.py generate-image "A cyberpunk city" --model "imagen-4.0-generate-001"
```

Use the specialized Nano Banana Pro model:

```bash
python scripts/gemini_client.py generate-image "A detailed banana concept art" --model "nano-banana-pro"
```

### Text-to-Speech (TTS)

Convert text to audio:

```bash
python scripts/gemini_client.py tts "Hello, this is Gemini speaking." --output "greeting.mp3"
```

### Embeddings

Generate vector embeddings for text retrieval tasks:

```bash
python scripts/gemini_client.py embed "The quick brown fox" --model "text-embedding-004"
```

### Multimodal & File Uploads

Upload files for use in prompts:

```bash
python scripts/gemini_client.py upload-file "data/chart.png"
```

Generate with image context:

```bash
python scripts/gemini_client.py generate "Describe this image" --image-path "data/chart.png"
```
