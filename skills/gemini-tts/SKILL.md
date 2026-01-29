---
name: gemini-tts
description: Generate speech from text using Google Gemini TTS models. Use for text-to-speech, audio generation, voice synthesis, multi-speaker conversations, and creating audio content. Supports multiple voices and streaming. Triggers on "text to speech", "TTS", "generate audio", "voice synthesis", "speak this text".
---

# Gemini Text-to-Speech

Generate natural-sounding speech from text using Gemini's TTS models with support for multiple voices and multi-speaker conversations.

## Prerequisites

- Set `GOOGLE_API_KEY` or `GEMINI_API_KEY` environment variable
- Install: `pip install google-genai`

## Quick Start

```python
import wave
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash-preview-tts",
    contents="Say cheerfully: Have a wonderful day!",
    config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Kore"
                )
            )
        )
    )
)

# Save to WAV file
audio_data = response.candidates[0].content.parts[0].inline_data.data
with wave.open("output.wav", "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(24000)
    wf.writeframes(audio_data)
```

## Available Scripts

- **scripts/tts.py** - Full-featured TTS with voice selection and multi-speaker support

## Models

| Model | Best For |
|-------|----------|
| `gemini-2.5-flash-preview-tts` | Fast TTS, general use |
| `gemini-2.5-pro-preview-tts` | Higher quality output |

## Available Voices

See [references/voices.md](references/voices.md) for the complete voice list.

Popular voices:
- **Kore** - Clear, professional
- **Puck** - Friendly, conversational
- **Charon** - Deep, authoritative
- **Fenrir** - Warm, expressive
- **Aoede** - Melodic, pleasant
- **Zephyr** - Light, airy

## Multi-Speaker Conversations

```python
prompt = """TTS the following conversation:
Joe: How's it going today?
Jane: Not too bad, how about you?"""

response = client.models.generate_content(
    model="gemini-2.5-flash-preview-tts",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=[
                    types.SpeakerVoiceConfig(
                        speaker="Joe",
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name="Kore"
                            )
                        )
                    ),
                    types.SpeakerVoiceConfig(
                        speaker="Jane",
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name="Puck"
                            )
                        )
                    ),
                ]
            )
        )
    )
)
```

## Streaming Audio

```python
for chunk in client.models.generate_content_stream(
    model="gemini-2.5-flash-preview-tts",
    contents="Long text to stream...",
    config=config
):
    if chunk.candidates and chunk.candidates[0].content.parts:
        part = chunk.candidates[0].content.parts[0]
        if part.inline_data:
            # Process audio chunk
            audio_chunk = part.inline_data.data
```

## Audio Format

- **Format**: Raw PCM (Linear16)
- **Sample rate**: 24000 Hz
- **Channels**: 1 (mono)
- **Bit depth**: 16-bit

## Token Limits

- **Input**: 8,192 tokens
- **Output**: 16,384 tokens
