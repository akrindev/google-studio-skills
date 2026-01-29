#!/usr/bin/env python3
"""Generate speech from text using Gemini TTS API.

Usage:
    python tts.py "Hello, world!"
    python tts.py "Welcome!" --voice Puck --output welcome
    python tts.py "Conversation text" --speakers "Joe:Kore,Jane:Puck"
    python tts.py "Long text" --stream
    python tts.py "Custom folder" --output-dir ./my-audio/

Requirements:
    pip install google-genai
"""

import argparse
import os
import sys
import wave
from pathlib import Path
from datetime import datetime

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


def save_wav(filename: str, audio_data: bytes, rate: int = 24000):
    """Save raw PCM audio data to WAV file."""
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(rate)
        wf.writeframes(audio_data)


def generate_tts(
    text: str,
    voice: str = "Kore",
    output_dir: str = "audio/",
    output_name: str = "tts_output",
    model: str = "gemini-2.5-flash-preview-tts",
    stream: bool = False,
    speakers: dict | None = None,
    use_timestamp: bool = True,
) -> str:
    """Generate speech from text.

    Args:
        text: Text to convert to speech
        voice: Voice name (for single speaker)
        output_dir: Directory to save audio file
        output_name: Base name for output file
        model: TTS model ID
        stream: Use streaming for long text
        speakers: Dict mapping speaker names to voices (for multi-speaker)
        use_timestamp: Add timestamp to filename

    Returns:
        Path to saved audio file
    """
    from google.genai import types

    client = get_client()

    # Build speech config
    if speakers:
        speaker_configs = [
            types.SpeakerVoiceConfig(
                speaker=name,
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=v)
                ),
            )
            for name, v in speakers.items()
        ]
        speech_config = types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=speaker_configs
            )
        )
    else:
        speech_config = types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)
            )
        )

    config = types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=speech_config,
    )

    contents = [types.Content(role="user", parts=[types.Part.from_text(text=text)])]

    all_audio = b""

    if stream:
        print("Streaming audio...")
        for chunk in client.models.generate_content_stream(
            model=model, contents=contents, config=config
        ):
            if chunk.candidates and chunk.candidates[0].content.parts:
                part = chunk.candidates[0].content.parts[0]
                if hasattr(part, "inline_data") and part.inline_data:
                    all_audio += part.inline_data.data
    else:
        response = client.models.generate_content(
            model=model, contents=contents, config=config
        )
        if response.candidates and response.candidates[0].content.parts:
            part = response.candidates[0].content.parts[0]
            if hasattr(part, "inline_data") and part.inline_data:
                all_audio = part.inline_data.data

    if all_audio:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        if use_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = output_name + "_" + timestamp
        else:
            filename = output_name

        if not filename.endswith(".wav"):
            filename += ".wav"

        full_path = output_path / filename
        save_wav(str(full_path), all_audio)
        print(f"Saved: {full_path}")
        return str(full_path)
    else:
        print("Error: No audio generated")
        sys.exit(1)


def parse_speakers(speakers_str: str) -> dict:
    """Parse speaker string like 'Joe:Kore,Jane:Puck' into dict."""
    speakers = {}
    for pair in speakers_str.split(","):
        if ":" in pair:
            name, voice = pair.split(":", 1)
            speakers[name.strip()] = voice.strip()
    return speakers


def main():
    parser = argparse.ArgumentParser(
        description="Generate speech from text using Gemini TTS"
    )
    parser.add_argument("text", help="Text to convert to speech")
    parser.add_argument(
        "--voice",
        "-v",
        default="Kore",
        help="Voice name (default: Kore). Options: Kore, Puck, Charon, Fenrir, Aoede, Zephyr, Sulafat",
    )
    parser.add_argument(
        "--output-dir",
        default="audio/",
        help="Output directory for audio file (default: audio/)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="tts_output",
        help="Base name for output file (default: tts_output). Timestamp will be appended automatically",
    )
    parser.add_argument(
        "--no-timestamp",
        action="store_true",
        help="Disable automatic timestamp in filename",
    )
    parser.add_argument(
        "--model",
        "-m",
        default="gemini-2.5-flash-preview-tts",
        help="Model ID (default: gemini-2.5-flash-preview-tts)",
    )
    parser.add_argument(
        "--stream", "-s", action="store_true", help="Use streaming for long text"
    )
    parser.add_argument(
        "--speakers", help="Multi-speaker mapping: 'Speaker1:Voice1,Speaker2:Voice2'"
    )

    args = parser.parse_args()

    speakers = parse_speakers(args.speakers) if args.speakers else None

    try:
        generate_tts(
            text=args.text,
            voice=args.voice,
            output_dir=args.output_dir,
            output_name=args.output,
            model=args.model,
            stream=args.stream,
            speakers=speakers,
            use_timestamp=not args.no_timestamp,
        )
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
