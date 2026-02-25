# aichat2md - Project Memory

**Project**: AI Chat to Markdown Converter
**Type**: Python CLI tool + PyPI package
**Version**: 1.3.2 | **Status**: Production-ready, published on PyPI

---

## Project Overview

Convert AI chat conversations (ChatGPT, Gemini, Doubao, Claude, etc.) to structured Markdown documents using AI-powered reorganization.

**Pipeline**: `Input → Extract (local, no AI) → Structurize (AI) → Save`

### Core Features

- **Dual extraction**: Playwright (URLs with JS rendering) + plistlib (Safari webarchive)
- **Multi-platform**: ChatGPT, Gemini, Doubao share links + webarchive/html files
- **Multi-API**: OpenAI-compatible backends (DeepSeek, OpenAI, Groq, custom)
- **Bilingual**: English/Chinese system prompts
- **PyPI package**: `pip install aichat2md` → global `aichat2md` command

---

## Project Structure

```
aichat2md/
├── aichat2md/
│   ├── __init__.py                 # Version string
│   ├── cli.py                      # Argument parsing, main entry
│   ├── config.py                   # Multi-API config, interactive setup
│   ├── structurizer.py             # OpenAI-compatible API calls
│   ├── extractors/
│   │   ├── playwright_extractor.py # URL extraction (Chromium)
│   │   └── webarchive_extractor.py # Binary plist parsing
│   └── prompts/
│       ├── system_prompt_en.txt
│       └── system_prompt_zh.txt
├── tests/                          # Pytest suite (11 tests)
│   ├── test_cli.py
│   └── test_config.py
└── pyproject.toml
```

---

## Configuration

**Location**: `~/.config/aichat2md/config.json`

```json
{
  "api_key": "sk-xxx",
  "api_base_url": "https://api.deepseek.com",
  "model": "deepseek-chat",
  "language": "en",
  "output_dir": "/Users/you/Downloads",
  "max_tokens": 4000,
  "temperature": 0.7
}
```

**API Presets**: `deepseek` (cost-effective) | `openai` | `groq` (fast) | `custom`

**Setup**: `aichat2md --setup` (interactive)

---

## Platform Extractors

### Supported Platforms

- **ChatGPT** - `chatgpt.com` share links
- **Gemini** - `gemini.google.com` or `g.co` (auto-redirects)
- **Doubao (豆包)** - `doubao.com` thread links
- **Claude** - NOT supported via URL (see Common Issues)

### Local File Formats

- **Safari** - `.webarchive` (best, preserves content perfectly)
- **Chrome/Edge** - `.mhtml` or `.html` (Save As → Web Page, Complete)
- **Firefox** - `.html` (Save Page As → Web Page, HTML only)

### Extraction Strategy (`playwright_extractor.py`)

```python
wait_times = {'claude': 5000, 'doubao': 3000, 'gemini': 5000, 'default': 2000}
# Gemini/Doubao: wait_until='load'; ChatGPT/others: wait_until='networkidle'
```

To add a new platform: update `_detect_platform()` and `_get_wait_time()`.

---

## Development Guide

### Local Setup

```bash
cd /Users/placenameday/R_Project/Tech/aichat2md
python3 -m venv venv && source venv/bin/activate
pip install -e .
playwright install chromium
pytest tests/ -v  # Should see: 11 passed
```

### Common Commands

```bash
# Dev
source venv/bin/activate
pytest tests/ -v
pytest -k test_validate

# Build & release
rm -rf dist/ build/ *.egg-info/
python -m build
twine upload --repository testpypi dist/*   # dry run
twine upload dist/*                          # production (interactive token)
```

### Code Conventions

1. **Config priority**: CLI args > config.json > defaults
2. **Error handling**: Specific messages (401 → "Check API key", 429 → "Rate limit")
3. **Path handling**: Always use `Path` objects, `expanduser` for `~`
4. **Tests**: Add tests for new features before merging

---

## Common Issues & Solutions

### "Prompt file not found" after PyPI install

Ensure `pyproject.toml` has:
```toml
[tool.setuptools.package-data]
aichat2md = ["prompts/*.txt"]
```
Verify: `unzip -l dist/*.whl | grep prompts`

### Other common fixes

| Issue | Fix |
|-------|-----|
| "Configuration file not found" | `aichat2md --setup` |
| "API authentication failed" | Check `~/.config/aichat2md/config.json` |
| Playwright browser missing | `playwright install chromium` |
| Import errors after editing | `pip install -e .` |
| Tests fail after changes | Update matching test file (`test_cli.py` / `test_config.py`) |

### Claude share links cannot be extracted

**Status**: Blocked. Cloudflare + cookie consent banner prevents React hydration; conversation data loads only after consent, but the consent button click handler doesn't fire in Playwright.

**Workaround**: Export manually from browser → `aichat2md <exported_file>`

**Unexplored approaches**:
1. `headless=False` — consent may work with real browser UI
2. Intercept consent API — discover endpoint/cookie via DevTools
3. `playwright-stealth` (npm) — more comprehensive anti-detection
4. `undetected-chromedriver` — better Cloudflare bypass
5. Direct API call to `claude.ai/api/share/{uuid}` with real browser cookies
6. Cookie name discovery — pre-set correct consent cookie in Playwright context

---

## File Modification Guidelines

- **`cli.py`**: Keep arg priority CLI > config > defaults; update `--help`; add tests
- **`config.py`**: Don't break existing configs; update `DEFAULT_CONFIG`; add tests
- **`structurizer.py`**: Maintain OpenAI compat; handle 401/429/500; test with multiple APIs
- **Prompts**: Test output quality; keep front matter consistent; sync EN/ZH conceptually

---

## Testing & Release

### Before Release Checklist
- [ ] `pytest tests/ -v` passes
- [ ] `aichat2md --help` accurate
- [ ] `aichat2md --version` correct
- [ ] `python -m build` succeeds
- [ ] `pip install dist/*.whl` works

### PyPI Release

```bash
# 1. Bump version in pyproject.toml AND aichat2md/__init__.py
# 2. git commit "chore: bump version to X.Y.Z"
rm -rf dist/ build/ *.egg-info/
python -m build
twine upload dist/*

# Tag and GitHub release
git tag vX.Y.Z && git push origin vX.Y.Z
gh release create vX.Y.Z --notes "..." dist/*.tar.gz dist/*.whl
```

**Critical**: README is bundled at build time — always rebuild after doc changes.

---

## Git Workflow

- `master`: Production-ready | `feature/xyz` | `bugfix/xyz`
- Commit types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
- Before committing: `pytest tests/ -v` + check no `pdb`/`breakpoint` in code

---

## Known Limitations & Roadmap

**Limitations**: Prompts optimized for ChatGPT format; very long conversations may hit token limits; requires Chromium.

**Planned**: Claude/Gemini native support, batch processing, conversation splitting, Ollama support.

---

## Dependencies

- `playwright>=1.40.0`, `requests>=2.31.0`, `yaspin>=3.0.0`
- Dev: `pytest>=9.0`, `build`, `twine`
- Python: 3.8+

---

**Last Updated**: 2026-02-25 | **Version**: 1.3.2
