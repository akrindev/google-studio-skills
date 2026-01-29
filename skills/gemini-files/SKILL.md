---
name: gemini-files
description: Upload and manage files using Google Gemini File API. Use for uploading images, audio, video, PDFs, and other files for use with Gemini models. Supports file upload, status checking, and file management. Triggers on "upload file", "file API", "upload image", "upload PDF", "upload video", "file management".
---

# Gemini File API

Upload and manage files for use with Gemini models. Supports images, audio, video, PDFs, and other file types.

## Prerequisites

- Set `GOOGLE_API_KEY` or `GEMINI_API_KEY` environment variable
- Install: `pip install google-genai`

## Quick Start

```python
from google import genai

client = genai.Client()

# Upload a file
my_file = client.files.upload(file="path/to/image.jpg")
print(f"Uploaded: {my_file.name}")
print(f"URI: {my_file.uri}")

# Use with generate_content
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=[my_file, "Describe this image"]
)
print(response.text)
```

## Available Scripts

- **scripts/upload.py** - Upload files to Gemini File API

## Supported File Types

| Type | Extensions | Max Size |
|------|------------|----------|
| Images | jpg, png, gif, webp | 20MB |
| Audio | mp3, wav, aac, flac | 25MB |
| Video | mp4, mov, avi, webm | 2GB |
| Documents | pdf, txt | 50MB |

## Upload with MIME Type

```python
from google.genai import types

# Specify MIME type explicitly
uploaded_file = client.files.upload(
    file="document.pdf",
    config=types.UploadFileConfig(
        mime_type="application/pdf",
        display_name="my-document"
    )
)
```

## Upload from URL

```python
import requests
import io

# Download from URL
url = "https://example.com/image.jpg"
response = requests.get(url)
file_io = io.BytesIO(response.content)

# Upload to Gemini
uploaded = client.files.upload(
    file=file_io,
    config=types.UploadFileConfig(mime_type="image/jpeg")
)
```

## Wait for Processing

Large files (especially video) may need processing time:

```python
import time

file = client.files.upload(file="video.mp4")

# Wait for file to be ready
while client.files.get(name=file.name).state != "ACTIVE":
    print("Processing...")
    time.sleep(2)

print("File ready!")
```

## File States

| State | Description |
|-------|-------------|
| `PROCESSING` | File is being processed |
| `ACTIVE` | File is ready for use |
| `FAILED` | Processing failed |

## List Files

```python
for file in client.files.list():
    print(f"{file.name}: {file.display_name} ({file.state})")
```

## Delete File

```python
client.files.delete(name=file.name)
```

## Use Cases

- **Multimodal prompts**: Upload images/videos for analysis
- **Document processing**: Upload PDFs for extraction
- **Audio transcription**: Upload audio for processing
- **Batch operations**: Pre-upload files for batch jobs
