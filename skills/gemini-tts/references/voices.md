# Available TTS Voices

## Voice List

| Voice Name | Characteristics |
|------------|-----------------|
| Aoede | Melodic, pleasant, smooth |
| Charon | Deep, authoritative, commanding |
| Fenrir | Warm, expressive, engaging |
| Kore | Clear, professional, neutral |
| Puck | Friendly, conversational, approachable |
| Zephyr | Light, airy, gentle |
| Sulafat | Calm, soothing |

## Voice Selection Tips

- **Professional/Business**: Kore, Charon
- **Casual/Friendly**: Puck, Fenrir
- **Storytelling**: Aoede, Fenrir
- **Meditation/Calm**: Sulafat, Zephyr
- **Announcements**: Charon, Kore

## Multi-Speaker Setup

For conversations, assign different voices to speakers:

```python
speaker_configs = [
    types.SpeakerVoiceConfig(
        speaker="Narrator",
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Aoede"
            )
        )
    ),
    types.SpeakerVoiceConfig(
        speaker="Character1",
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Kore"
            )
        )
    ),
    types.SpeakerVoiceConfig(
        speaker="Character2",
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Puck"
            )
        )
    ),
]
```

## Text Format for Multi-Speaker

Use speaker labels in your text:

```
Narrator: Once upon a time...
Character1: Hello there!
Character2: Nice to meet you!
```

The model will automatically use the assigned voices for each speaker.
