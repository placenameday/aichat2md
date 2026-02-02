# ChatGPT2MD

Convert ChatGPT share links and Safari webarchive files to structured Markdown documents using AI.

## Features

- 📡 Extract from ChatGPT share URLs (with full JS rendering)
- 📄 Extract from Safari .webarchive files (offline)
- 🤖 AI-powered structurization with DeepSeek API
- 📝 Clean, knowledge-focused output (no chat format)
- ⚙️ Simple configuration with sensible defaults

## Installation

### 1. Clone the repository

```bash
git clone <repo-url>
cd chatgpt2md
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Playwright browsers

```bash
playwright install chromium
```

### 4. Configure the tool

```bash
python chatgpt2md.py --setup
```

You'll be prompted for:
- **DeepSeek API key** (get one at https://platform.deepseek.com)
- **Output directory** (default: ~/Downloads)

## Usage

### Extract from URL

```bash
python chatgpt2md.py https://chatgpt.com/share/xxx
```

Output: `~/Downloads/2024-02-02-<generated-title>.md`

### Extract from webarchive

```bash
python chatgpt2md.py ~/Downloads/chat.webarchive
```

Output: `~/Downloads/chat.md` (same directory as input)

## Output Format

Generated Markdown documents include:

```markdown
---
技术标签: [Python, API, Web]
日期: 2024-02-02
来源: https://chatgpt.com/share/xxx
---

# Document Title

## 摘要
Brief summary of the conversation content

## 关键主题
- Key theme 1
- Key theme 2

## Knowledge Section 1
Reorganized content in tutorial/documentation style

## Code Examples
```python
# Extracted code with explanations
```
```

## Configuration

Edit `config.json` to customize:

```json
{
  "deepseek_api_key": "sk-xxx",
  "output_dir": "~/Downloads",
  "model": "deepseek-chat",
  "max_tokens": 4000,
  "temperature": 0.7
}
```

## Requirements

- Python 3.8+
- DeepSeek API key (https://platform.deepseek.com)
- Chromium browser (auto-installed by Playwright)

## Troubleshooting

### "Page load timeout"
- Check your network connection
- Verify the ChatGPT share URL is valid and accessible

### "API authentication failed"
- Verify your DeepSeek API key in `config.json`
- Check https://platform.deepseek.com for API status

### "Invalid webarchive"
- Ensure the file is saved as "Web Archive" format in Safari
- Try re-saving the page

## License

MIT
