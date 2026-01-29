# Gemini Models Reference (January 2026)

## Text Generation Models

### Gemini 3 Flash Preview (Recommended Default)
- **Model ID**: `gemini-3-flash-preview`
- **Best for**: Fast, agentic workflows, coding, multi-turn chat
- **Context**: 1,048,576 tokens input / 65,536 tokens output
- **Inputs**: Text, images, video, audio, PDF
- **Output**: Text
- **Features**: Configurable thinking levels, multimodal, agentic capabilities
- **Released**: December 2025
- **Knowledge cutoff**: January 2025

### Gemini 3 Pro Preview (Most Intelligent)
- **Model ID**: `gemini-3-pro-preview`
- **Best for**: Most intelligent multimodal, complex reasoning, vibe-coding
- **Context**: 1,048,576 tokens input / 65,536 tokens output
- **Inputs**: Text, images, video, audio, PDF
- **Output**: Text
- **Features**: Advanced multimodal understanding, agentic capabilities
- **Latest update**: November 2025
- **Knowledge cutoff**: January 2025

### Gemini 2.5 Flash (Stable)
- **Model ID**: `gemini-2.5-flash`
- **Best for**: Stable, general-purpose tasks, cost-effective
- **Context**: 1,048,576 tokens input / 65,536 tokens output
- **Inputs**: Text, images, video, audio
- **Output**: Text
- **Features**: Thinking mode, function calling, code execution, Google Search grounding, TTS support
- **Latest update**: June 2025

## Image Generation Models

### Gemini 3 Pro Image Preview (Highest Quality)
- **Model ID**: `gemini-3-pro-image-preview`
- **Nickname**: "Nano Banana Pro"
- **Best for**: Professional asset production, advanced text rendering
- **Sizes**: 1K, 2K, 4K
- **Features**: Google Search grounding, highest resolution
- **Aspect ratios**: 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9

### Gemini 2.5 Flash Image (Fast)
- **Model ID**: `gemini-2.5-flash-image`
- **Nickname**: "Nano Banana"
- **Best for**: High-volume, low-latency image generation
- **Aspect ratios**: 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9

### Imagen 4 (Stable)
- **Model ID**: `imagen-4.0-generate-001`
- **Best for**: Photorealistic images
- **Sizes**: 1K, 2K
- **Note**: Imagen 3 has been shut down

## Text-to-Speech Models

### Gemini 2.5 Flash TTS
- **Model ID**: `gemini-2.5-flash-preview-tts`
- **Input**: 32,000 tokens context
- **Features**: Multi-speaker, 24 languages, style/tone/pace control
- **Latest update**: December 2025

### Gemini 2.5 Pro TTS
- **Model ID**: `gemini-2.5-pro-preview-tts`
- **Input**: 32,000 tokens context
- **Features**: Multi-speaker, enhanced expressivity
- **Latest update**: December 2025

## Embedding Models

### Gemini Embedding (Current)
- **Model ID**: `gemini-embedding-001`
- **Output dimensions**: 768, 1536, or 3072 (configurable)
- **Default dimension**: 3072

### Text Embedding (DEPRECATED)
- **Model ID**: `text-embedding-004`
- **Status**: SHUT DOWN January 14, 2026
- **Use `gemini-embedding-001` instead**

## Model Selection Guide

| Use Case | Recommended Model |
|----------|-------------------|
| Most intelligent | `gemini-3-pro-preview` |
| Fast responses | `gemini-2.5-flash` |
| Complex reasoning | `gemini-2.5-pro` |
| Cost-sensitive | `gemini-2.5-flash-lite` |
| 4K images | `gemini-3-pro-image-preview` |
| Fast images | `gemini-2.5-flash-image` |
| Text-to-speech | `gemini-2.5-flash-preview-tts` |
| Embeddings | `gemini-embedding-001` |

## Aliases

- `gemini-flash-latest` - Points to latest stable Flash model
- Updates communicated 2 weeks in advance via email

## Listing Available Models

```python
from google import genai

client = genai.Client()
for model in client.models.list():
    print(model.name)
```
