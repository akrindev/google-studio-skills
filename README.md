# Google AI Agent Skills

Agent Skills for Google AI services. These skills teach AI agents (Claude Code, Gemini CLI, Cursor, OpenCode, etc.) how to use Google's Gemini API effectively.

Built following the [Agent Skills](https://agentskills.io) open standard.

## Available Skills

| Skill               | Description                          |
| ------------------- | ------------------------------------ |
| `gemini-text`       | Text generation with Gemini models   |
| `gemini-image`      | Image generation with Gemini/Imagen  |
| `gemini-tts`        | Text-to-speech synthesis             |
| `gemini-batch`      | Batch processing for large workloads |
| `gemini-embeddings` | Text embeddings for semantic search  |
| `gemini-files`      | File upload to Gemini Files API      |

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

### 1. Skills CLI (`npx skills`)

The easiest way to use these skills is via the [Skills CLI](https://skills.sh). It automatically installs skills into your `.agent/skills` directory for discovery by agents like Claude Code or Gemini CLI.

```bash
# Install a specific skill
npx skills add https://github.com/akrindev/google-studio-skills/tree/main/skills/gemini-text

# Install the entire collection
npx skills add akrindev/google-studio-skills
```

### 2. ClawdHub & Moltbot

[Moltbot](https://molt.bot) (formerly Clawdbot) is a local-first AI assistant. You can manage and run these skills using the `clawdhub` CLI.

**Installation & Setup:**
```bash
# Install Moltbot and ClawdHub CLI
npm install -g moltbot clawdhub

# Initialize Moltbot
moltbot onboard
```

**Manage Skills:**
```bash
# Search for Gemini skills on ClawdHub
clawdhub search gemini

# Install a skill to your workspace (~/molt/skills/)
clawdhub install gemini-text --workdir ~/molt
```

**Running Skills:**
Once installed, interact with Moltbot via the terminal or connected chat apps (WhatsApp/Telegram). Simply ask:
> "Molt, use the gemini-text skill to summarize this document."

### 3. Manual Installation (Claude Code / Gemini CLI / OpenCode)

These agents automatically discover skills in `skills/` directories. You can manually point your agent to this repository:

```bash
# Clone the repository
git clone https://github.com/akrindev/google-studio-skills.git

# Navigate to your project and the agent will discover skills in the adjacent folder
# or add the path to your agent's configuration
```

### 4. Discovery on Skills.sh

Browse the full directory of available skills and see community rankings at [skills.sh](https://skills.sh).

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

| Capability | Default Model                  | Notes                     |
| ---------- | ------------------------------ | ------------------------- |
| Text       | `gemini-3-flash-preview`       | Fast, agentic, multimodal |
| Image      | `gemini-3-pro-image-preview`   | Up to 4K resolution       |
| TTS        | `gemini-2.5-flash-preview-tts` | Multiple voices           |
| Embeddings | `gemini-embedding-001`         | 3072 dimensions           |

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
