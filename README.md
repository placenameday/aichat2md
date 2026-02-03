# aichat2md

Convert AI chat conversations to structured Markdown documents.

## Features

- 🌐 **Extract from URLs** - ChatGPT, Gemini, Doubao share links (with JS rendering via Playwright)
- 📄 **Extract from webarchive** - Safari .webarchive files (offline mode)
- 🤖 **Multiple AI backends** - DeepSeek, OpenAI, Groq, or any OpenAI-compatible API
- 🌍 **Bilingual support** - English/Chinese prompts
- 📝 **Clean output** - Knowledge-focused Markdown, not chat logs
- ⚡ **Simple CLI** - pip-installable, one-time setup

## Quick Start

```bash
# Install
pip install aichat2md

# Configure (one-time setup)
aichat2md --setup

# Convert a ChatGPT share URL
aichat2md https://chatgpt.com/share/xxx

# Convert a webarchive file
aichat2md ~/Downloads/chat.webarchive
```

## Supported Platforms

- **ChatGPT** - chatgpt.com share links
- **Gemini** - gemini.google.com or g.co share links
- **Doubao (豆包)** - doubao.com share links
- **Webarchive** - Safari exported .webarchive files (any platform)

### Usage Examples

```bash
# ChatGPT
aichat2md https://chatgpt.com/share/xxx

# Gemini (supports both long and short URLs)
aichat2md https://gemini.google.com/share/xxx
aichat2md https://g.co/gemini/share/xxx

# Doubao
aichat2md https://www.doubao.com/thread/xxx

# Webarchive file
aichat2md ~/Downloads/conversation.webarchive
```

## Supported AI Backends

- **DeepSeek** (default) - Cost-effective, Chinese service
- **OpenAI** - GPT-4o-mini, GPT-4
- **Groq** - Fast inference with Llama models
- **Custom** - Any OpenAI-compatible API

## Installation

### Prerequisites

- Python 3.8 or higher
- Playwright (automatically installed, but requires browser setup)

### Install from PyPI

```bash
pip install aichat2md
```

### Install Playwright browsers

```bash
playwright install chromium
```

### First-time Setup

```bash
aichat2md --setup
```

You'll be prompted to:
1. Select your AI provider (DeepSeek, OpenAI, Groq, or custom)
2. Enter your API key
3. Choose prompt language (English or Chinese)
4. Set output directory (default: ~/Downloads)

## Usage

### Basic Usage

```bash
# Convert from URL (uses configured output directory)
aichat2md https://chatgpt.com/share/xxx

# Convert from webarchive (outputs to same directory as input)
aichat2md ~/Downloads/chat.webarchive
```

### Override Language

```bash
# Use Chinese prompts (even if English is configured)
aichat2md <url> --lang zh

# Use English prompts
aichat2md <url> --lang en
```

### Custom Output Path

```bash
# Specify output file
aichat2md <url> -o ~/Documents/my-notes.md
aichat2md <url> --output ~/Documents/my-notes.md
```

### Override Model

```bash
# Use a different model than configured
aichat2md <url> --model gpt-4o
aichat2md <url> --model deepseek-chat
```

### Version Info

```bash
aichat2md --version
```

## Configuration

Configuration is stored in `~/.config/aichat2md/config.json` (cross-platform).

### Example Config

```json
{
  "api_key": "sk-your-api-key",
  "api_base_url": "https://api.deepseek.com",
  "model": "deepseek-chat",
  "language": "en",
  "output_dir": "/Users/you/Downloads",
  "max_tokens": 4000,
  "temperature": 0.7
}
```

### Reconfigure

```bash
aichat2md --setup
```

## Output Format

The tool converts chat conversations into structured Markdown with:

- **Front matter** - Tags, date, source
- **Summary** - 2-3 sentence overview
- **Key topics** - Bullet point list
- **Knowledge sections** - Reorganized content with logical headings
- **Code examples** - Extracted code blocks with comments

### Example Output

```markdown
---
tags: [Python, API, Web]
date: 2026-02-02
source: https://chatgpt.com/share/xxx
---

# Building REST APIs with FastAPI

## Summary
This document covers building production-ready REST APIs using FastAPI...

## Key Topics
- API design patterns
- Request validation
- Error handling

## API Design Principles
...

## Code Examples
\```python
from fastapi import FastAPI
app = FastAPI()
...
\```
```

## How It Works

1. **Extract** - Playwright (URLs) or plistlib (webarchive) extracts raw text
2. **Structurize** - AI API reorganizes into knowledge document
3. **Save** - Auto-generated filename or specified path

### Why Two-Stage Processing?

- **Stage 1 (Extract)** - No AI tokens used, just HTML parsing
- **Stage 2 (Structurize)** - AI organizes content efficiently

This saves costs and allows local caching of extracted content.

## Development

### Local Installation

```bash
# Clone repository
git clone https://github.com/yourusername/aichat2md.git
cd aichat2md

# Install in editable mode
pip install -e .

# Install Playwright
playwright install chromium
```

### Run Tests

```bash
pip install pytest
pytest tests/
```

### Build Package

```bash
pip install build
python -m build
```

## Troubleshooting

### "Configuration file not found"

Run `aichat2md --setup` to create configuration.

### "API authentication failed"

Check your API key in `~/.config/aichat2md/config.json`.

### Playwright errors

Install browsers: `playwright install chromium`

### Empty output

The conversation might be too short or the AI response failed. Check error messages.

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file.

## Links

- [GitHub Repository](https://github.com/yourusername/aichat2md)
- [Issue Tracker](https://github.com/yourusername/aichat2md/issues)
- [中文文档](README_zh.md)

## Acknowledgments

- [Playwright](https://playwright.dev/) - Web automation
- [DeepSeek](https://www.deepseek.com/) - Cost-effective AI API
- [OpenAI](https://openai.com/) - API compatibility standard
