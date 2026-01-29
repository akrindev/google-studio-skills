---
name: gemini-image
description: Generate images using Google Gemini and Imagen models. Use for AI image generation, text-to-image, creating visuals from prompts, generating multiple images, custom aspect ratios, and high-resolution output up to 4K. Triggers on "generate image", "create image", "imagen", "text to image", "AI art", "nano banana".
---

# Gemini Image Generation

Generate high-quality images from text prompts using Google's Gemini and Imagen models.

## Prerequisites

- Set `GOOGLE_API_KEY` or `GEMINI_API_KEY` environment variable
- Install: `pip install google-genai pillow`

## Quick Start

```python
from google import genai
from google.genai import types

client = genai.Client()

# Using Gemini 3 Pro Image (recommended)
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="A futuristic city at sunset with flying cars"
)

# Or using Imagen 4
response = client.models.generate_images(
    model="imagen-4.0-generate-001",
    prompt="A futuristic city at sunset with flying cars",
    config=types.GenerateImagesConfig(number_of_images=1)
)
```

## Available Scripts

- **scripts/generate_image.py** - Full-featured image generation with all options

## Models

### Gemini 3 Pro Image Preview (Recommended - Highest Quality)
- **Model ID**: `gemini-3-pro-image-preview`
- **Nickname**: "Nano Banana Pro"
- **Best for**: Professional assets, advanced text rendering, up to 4K
- **Sizes**: 1K, 2K, 4K
- **Aspect ratios**: 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9
- **Features**: Google Search grounding for references

### Gemini 2.5 Flash Image (Fast)
- **Model ID**: `gemini-2.5-flash-image`
- **Nickname**: "Nano Banana"
- **Best for**: High-volume, low-latency image generation
- **Aspect ratios**: 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9

### Imagen 4 (Stable)
- **Model ID**: `imagen-4.0-generate-001`
- **Best for**: Photorealistic images
- **Sizes**: 1K, 2K
- **Aspect ratios**: 1:1, 3:4, 4:3, 9:16, 16:9
- **Max images**: 4 per request
- **Note**: Imagen 3 has been shut down

## Usage Examples

### Generate with Imagen 4

```python
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_images(
    model="imagen-4.0-generate-001",
    prompt="Robot holding a red skateboard",
    config=types.GenerateImagesConfig(
        number_of_images=4,
        aspect_ratio="16:9",
        image_size="2K",
        person_generation="allow_adult"
    )
)

for i, img in enumerate(response.generated_images):
    with open(f"image_{i}.png", "wb") as f:
        f.write(img.image.image_bytes)
```

### Generate with Gemini 3 Pro (4K)

```python
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="Create a nano banana dish in a fancy restaurant",
    config=types.GenerateContentConfig(
        generation_config={
            "image_config": {
                "aspect_ratio": "16:9",
                "image_size": "4K"
            }
        }
    )
)

# Extract image from response
image_data = response.candidates[0].content.parts[0].inline_data.data
```

## Configuration Options

### Imagen 4 Config

| Parameter | Type | Description |
|-----------|------|-------------|
| `number_of_images` | int | 1-4 images per request |
| `image_size` | str | "1K" or "2K" |
| `aspect_ratio` | str | "1:1", "3:4", "4:3", "9:16", "16:9" |
| `person_generation` | str | "dont_allow", "allow_adult", "allow_all" |

### Gemini 3 Pro Config

| Parameter | Type | Description |
|-----------|------|-------------|
| `image_size` | str | "1K", "2K", or "4K" |
| `aspect_ratio` | str | Multiple ratios including 21:9 |

## Resolution Reference

### Imagen 4
| Aspect Ratio | 1K Resolution | 2K Resolution |
|--------------|---------------|---------------|
| 1:1 | 1024x1024 | 2048x2048 |
| 16:9 | 1376x768 | 2752x1536 |
| 9:16 | 768x1376 | 1536x2752 |

### Gemini 3 Pro Image Preview
| Aspect Ratio | 1K | 2K | 4K |
|--------------|-----|-----|-----|
| 1:1 | 1024x1024 | 2048x2048 | 4096x4096 |
| 16:9 | 1376x768 | 2752x1536 | 5504x3072 |

## Notes

- Imagen supports **English prompts only**
- All generated images include **SynthID watermark** for authenticity
- `person_generation="allow_all"` is restricted in EU, UK, CH, MENA regions
