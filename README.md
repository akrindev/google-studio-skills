# Google AI Agent Skills

Agent Skills for Google AI services. These skills teach AI agents (Claude Code, Gemini CLI, Cursor, OpenCode, etc.) how to use Google's Gemini API effectively.

Built following the [Agent Skills](https://agentskills.io) open standard.

## Available Skills

| Skill | Description |
|-------|-------------|
| `gemini-text` | Text generation with Gemini models |
| `gemini-image` | Image generation with Gemini/Imagen |
| `gemini-tts` | Text-to-speech synthesis |
| `gemini-batch` | Batch processing for large workloads |
| `gemini-embeddings` | Text embeddings for semantic search |
| `gemini-files` | File upload to Gemini Files API |

## Setup

### 1. Get API Key

Get your API key from [Google AI Studio](https://aistudio.google.com/apikey).

### 2. Set Environment Variable

```bash
export GEMINI_API_KEY="your-api-key"
```

Or create a `.env` file:
```
GEMINI_API_KEY=your-api-key
```

### 3. Install SDK

```bash
pip install google-genai
```

## Usage with AI Agents

### Claude Code / Gemini CLI / OpenCode

These agents automatically discover skills in `skills/` directories. Point your agent to this repository:

```bash
# Clone the repository
git clone https://github.com/user/google-skills.git

# Navigate to a project and the agent will discover skills
cd your-project
```

Or add to your agent's configuration to include this skills directory.

### Manual Usage

Each skill contains standalone Python scripts that can be run directly:

```bash
# Text generation
python skills/gemini-text/scripts/generate.py "Explain quantum computing"

# Image generation
python skills/gemini-image/scripts/generate_image.py "A sunset over mountains"

# Text-to-speech
python skills/gemini-tts/scripts/tts.py "Hello world" --voice Kore

# Embeddings
python skills/gemini-embeddings/scripts/embed.py "semantic search query"
```

## Default Models (January 2026)

| Capability | Default Model | Notes |
|------------|---------------|-------|
| Text | `gemini-3-flash-preview` | Fast, agentic, multimodal |
| Image | `gemini-3-pro-image-preview` | Up to 4K resolution |
| TTS | `gemini-2.5-flash-preview-tts` | Multiple voices |
| Embeddings | `gemini-embedding-001` | 3072 dimensions |

## Skill Structure

Each skill follows the Agent Skills specification:

```
skills/gemini-text/
├── SKILL.md           # Instructions for AI agents
├── scripts/           # Executable Python scripts
│   └── generate.py
└── references/        # Additional documentation
    └── models.md
```

## Development

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install google-genai

# Format code
ruff format skills/

# Lint code
ruff check skills/
```

## License

MIT
