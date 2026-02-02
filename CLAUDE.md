# aichat2md - Project Memory

**Project**: AI Chat to Markdown Converter
**Type**: Python CLI tool + PyPI package
**Status**: Production-ready, published on PyPI

---

## Project Overview

Convert AI chat conversations (ChatGPT, Claude, etc.) to structured Markdown documents using AI-powered reorganization.

### Core Features

- **Dual extraction**: Playwright (URLs with JS rendering) + plistlib (Safari webarchive)
- **Multi-API**: OpenAI-compatible backends (DeepSeek, OpenAI, Groq, custom)
- **Bilingual**: English/Chinese system prompts
- **PyPI package**: `pip install aichat2md` → global `aichat2md` command
- **Smart output**: Knowledge documents, not chat logs

### Architecture

```
Input → Extract (no AI) → Structurize (AI) → Save
```

**Why two-stage?**
- Extract: Local processing, no token cost
- Structurize: AI reorganizes into knowledge format
- Allows caching extracted content

---

## Project Structure

```
aichat2md/
├── aichat2md/                      # Main package
│   ├── __init__.py                 # Version: 1.0.0
│   ├── cli.py                      # Argument parsing, main entry
│   ├── config.py                   # Multi-API config, interactive setup
│   ├── structurizer.py             # OpenAI-compatible API calls
│   ├── extractors/
│   │   ├── playwright_extractor.py # URL extraction (Chromium)
│   │   └── webarchive_extractor.py # Binary plist parsing
│   └── prompts/
│       ├── system_prompt_en.txt    # English prompt
│       └── system_prompt_zh.txt    # Chinese prompt
├── tests/                          # Pytest suite (11 tests)
│   ├── test_cli.py
│   └── test_config.py
├── pyproject.toml                  # Modern Python packaging
├── README.md / README_zh.md        # Documentation
└── LICENSE                         # MIT
```

---

## Configuration

**Location**: `~/.config/aichat2md/config.json` (cross-platform)

**Structure**:
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

**API Presets**:
- `deepseek`: Cost-effective, Chinese service
- `openai`: GPT-4o-mini/GPT-4
- `groq`: Fast inference (Llama)
- `custom`: Any OpenAI-compatible API

**Setup**: `aichat2md --setup` (interactive)

---

## Development Guide

### Local Setup

```bash
# Clone and setup
cd /Users/placenameday/R_Project/Tech/aichat2md
python3 -m venv venv
source venv/bin/activate

# Install in editable mode
pip install -e .

# Install Playwright browser
playwright install chromium

# Run tests
pytest tests/ -v  # Should see: 11 passed
```

### Common Commands

```bash
# Development
source venv/bin/activate           # Activate venv
aichat2md --version               # Verify installation
aichat2md --help                  # Check CLI

# Testing
pytest tests/ -v                  # Run all tests
pytest tests/test_cli.py -v      # Specific test file
pytest -k test_validate          # By name pattern

# Building
pip install build twine
python -m build                   # Creates dist/
ls dist/                          # .tar.gz + .whl

# TestPyPI (dry run)
twine upload --repository testpypi dist/*
pip install -i https://test.pypi.org/simple/ aichat2md

# Production PyPI
twine upload dist/*
```

### Code Conventions

1. **Config priority**: CLI args > config.json > defaults
2. **Error handling**: Specific messages (401 → "Check API key", 429 → "Rate limit")
3. **Path handling**: Always use `Path` objects, expanduser for `~`
4. **Cross-platform**: Test config paths work on Windows/Mac/Linux
5. **Tests**: Add tests for new features before merging

### Adding New API Provider

1. Add preset to `config.py`:
```python
API_PRESETS = {
    "newapi": {
        "api_base_url": "https://api.example.com",
        "model": "model-name",
        "description": "New API (description)"
    }
}
```

2. Test with `aichat2md --setup`

### Adding New Language

1. Create prompt: `aichat2md/prompts/system_prompt_{code}.txt`
2. Update CLI: `--lang` choices in `cli.py`
3. Test: `aichat2md <url> --lang {code}`

---

## Key Design Decisions

### Why OpenAI-Compatible?

- **Standardization**: Most APIs follow OpenAI format
- **Flexibility**: Easy to add new providers
- **No vendor lock-in**: Switch APIs without code changes

### Why Separate Prompts?

- **Maintainability**: Edit prompts without touching code
- **Localization**: Add languages without rebuilding
- **Version control**: Track prompt changes separately

### Why Two-Stage Processing?

- **Cost**: Extract locally (no API calls)
- **Caching**: Reuse extracted content with different prompts
- **Debugging**: Inspect raw extraction before AI processing

### Why Cross-Platform Config?

- **Standard**: Follows XDG Base Directory spec
- **Security**: Separate from project (don't commit API keys)
- **Portability**: Works on all platforms

---

## Common Issues & Solutions

### "Configuration file not found"

**Fix**: Run `aichat2md --setup` to create config

### "API authentication failed"

**Fix**: Check API key in `~/.config/aichat2md/config.json`

### Playwright browser not installed

**Fix**: `playwright install chromium`

### Import errors after editing

**Fix**: Reinstall: `pip install -e .`

### Tests fail after changes

**Fix**: Check if you modified:
- Config structure → Update `test_config.py`
- CLI args → Update `test_cli.py`
- API format → Update `structurizer.py`

---

## File Modification Guidelines

### When editing `cli.py`:
- Keep argument priority: CLI > config > defaults
- Maintain backward compatibility with old configs
- Update `--help` examples
- Add tests to `test_cli.py`

### When editing `config.py`:
- Don't break existing config files
- Migrate old formats gracefully
- Update `DEFAULT_CONFIG`
- Add tests to `test_config.py`

### When editing `structurizer.py`:
- Maintain OpenAI API compatibility
- Handle all common error codes (401, 429, 500)
- Keep prompt loading flexible
- Test with multiple APIs

### When editing prompts:
- Test output quality manually
- Ensure front matter format stays consistent
- Keep both languages in sync (conceptually)

---

## Testing Strategy

### Unit Tests
- `test_cli.py`: Filename sanitization, markdown parsing
- `test_config.py`: Config validation, API presets

### Integration Tests (Manual)
```bash
# Test extraction
aichat2md https://chatgpt.com/share/xxx

# Test webarchive
aichat2md ~/Downloads/sample.webarchive

# Test language override
aichat2md <url> --lang zh

# Test output override
aichat2md <url> -o /tmp/test.md

# Test model override
aichat2md <url> --model gpt-4o
```

### Before Release Checklist
- [ ] All tests pass: `pytest tests/ -v`
- [ ] CLI help accurate: `aichat2md --help`
- [ ] Setup works: `aichat2md --setup`
- [ ] Version correct: `aichat2md --version`
- [ ] Build succeeds: `python -m build`
- [ ] Installation works: `pip install dist/*.whl`

---

## Git Workflow

### Branch Strategy
- `master`: Production-ready code
- Feature branches: `feature/xyz`
- Bugfix branches: `bugfix/xyz`

### Commit Message Format
```
type: short description

- Detailed change 1
- Detailed change 2

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Types**: feat, fix, docs, refactor, test, chore

### Before Committing
```bash
# Run tests
pytest tests/ -v

# Check no debug code
grep -r "print\|pdb\|breakpoint" aichat2md/

# Stage changes
git add -A
git status
```

---

## PyPI Release Process

### 1. Pre-release
```bash
# Update version in aichat2md/__init__.py
# Update CHANGELOG.md (if exists)
# Commit: "chore: bump version to X.Y.Z"
```

### 2. Build
```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info/

# Build fresh
python -m build
```

### 3. Test on TestPyPI
```bash
twine upload --repository testpypi dist/*

# Test in clean venv
python -m venv test-venv
source test-venv/bin/activate
pip install -i https://test.pypi.org/simple/ aichat2md
aichat2md --version
```

### 4. Production Release
```bash
twine upload dist/*
```

### 5. GitHub Release
```bash
git tag v1.0.0
git push origin v1.0.0

# Create release on GitHub with:
# - Tag: v1.0.0
# - Attach: dist/*.tar.gz and dist/*.whl
```

---

## Performance Considerations

### Token Usage
- **Extract**: 0 tokens (local processing)
- **Structurize**: ~1000-4000 tokens/conversation
- **Cost**: Depends on API (DeepSeek ~$0.001/call)

### Processing Time
- **URL extraction**: 5-10s (Playwright startup + JS render)
- **Webarchive extraction**: <1s (local file parsing)
- **AI structurization**: 10-30s (API latency + generation)

### Optimization Tips
- Use DeepSeek for cost efficiency
- Cache extracted content for prompt iterations
- Split very long conversations (>20K tokens)

---

## Known Limitations

1. **ChatGPT focus**: Prompts optimized for ChatGPT format
2. **Token limits**: Very long conversations may fail
3. **Playwright dependency**: Requires Chromium installation
4. **API rate limits**: Respect provider limits

---

## Future Enhancements

### Planned (Optional)
- [ ] Claude/Gemini native support
- [ ] Batch processing mode
- [ ] Custom output templates
- [ ] Conversation splitting for long chats
- [ ] Local LLM support (Ollama)
- [ ] Web UI (Flask/FastAPI)

### Not Planned
- Real-time streaming
- Cloud hosting
- Mobile app

---

## Dependencies

**Core**:
- `playwright>=1.40.0` - Browser automation
- `requests>=2.31.0` - HTTP client

**Dev**:
- `pytest>=9.0` - Testing
- `build` - Package building
- `twine` - PyPI uploads

**Python**: 3.8+ (tested on 3.8, 3.9, 3.10, 3.11, 3.12, 3.13)

---

## Contact & Support

**Repository**: https://github.com/yourusername/aichat2md
**Issues**: https://github.com/yourusername/aichat2md/issues
**License**: MIT

---

## Quick Reference

### File Locations
- **Config**: `~/.config/aichat2md/config.json`
- **Output**: `~/Downloads/` (default) or `--output` path
- **Logs**: Stderr (errors only)

### Common Workflows

**First time user**:
```bash
pip install aichat2md
aichat2md --setup
aichat2md https://chatgpt.com/share/xxx
```

**Development**:
```bash
cd aichat2md
source venv/bin/activate
pytest tests/ -v
aichat2md --help
```

**Release**:
```bash
python -m build
twine upload dist/*
git tag vX.Y.Z
```

---

**Last Updated**: 2026-02-02
**Version**: 1.0.0
**Status**: Production-ready
