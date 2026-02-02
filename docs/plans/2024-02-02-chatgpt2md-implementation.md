# ChatGPT2MD Tool Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python CLI tool that extracts ChatGPT share links or webarchive files and converts them to structured Markdown using DeepSeek API.

**Architecture:** Two-stage pipeline: (1) text extraction without AI (Playwright for URLs, plistlib for webarchives), (2) AI structurization via DeepSeek API. Config-driven with sensible defaults.

**Tech Stack:** Python 3.8+, Playwright, DeepSeek API, plistlib (stdlib)

---

## Task 1: Project Structure and Dependencies

**Files:**
- Create: `chatgpt2md.py`
- Create: `requirements.txt`
- Create: `extractors/__init__.py`
- Create: `extractors/playwright_extractor.py`
- Create: `extractors/webarchive_extractor.py`
- Create: `structurizer.py`
- Create: `prompt_template.py`
- Create: `config_manager.py`

**Step 1: Create project structure**

```bash
mkdir -p extractors
touch chatgpt2md.py
touch requirements.txt
touch extractors/__init__.py
touch extractors/playwright_extractor.py
touch extractors/webarchive_extractor.py
touch structurizer.py
touch prompt_template.py
touch config_manager.py
```

**Step 2: Write requirements.txt**

Create `requirements.txt`:
```txt
playwright>=1.40.0
requests>=2.31.0
```

**Step 3: Verify structure**

Run: `ls -R`
Expected: See all created files

**Step 4: Commit**

```bash
git init
git add .
git commit -m "feat: initial project structure and dependencies"
```

---

## Task 2: Config Manager Module

**Files:**
- Modify: `config_manager.py`

**Step 1: Write config manager implementation**

```python
import json
from pathlib import Path
from typing import Dict, Any


CONFIG_FILE = Path(__file__).parent / 'config.json'


def get_default_output_dir() -> str:
    """Get platform-specific default downloads directory."""
    return str(Path.home() / "Downloads")


def create_default_config() -> Dict[str, Any]:
    """Create default configuration."""
    return {
        "deepseek_api_key": "",
        "output_dir": get_default_output_dir(),
        "model": "deepseek-chat",
        "max_tokens": 4000,
        "temperature": 0.7
    }


def setup_config():
    """Interactive config setup."""
    print("=== ChatGPT2MD Configuration Setup ===\n")

    api_key = input("Enter your DeepSeek API key: ").strip()
    output_dir = input(f"Output directory (default: {get_default_output_dir()}): ").strip()

    config = create_default_config()
    config["deepseek_api_key"] = api_key
    if output_dir:
        config["output_dir"] = output_dir

    CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding='utf-8')
    print(f"\n✓ Configuration saved to {CONFIG_FILE}")


def load_config() -> Dict[str, Any]:
    """Load configuration from file."""
    if not CONFIG_FILE.exists():
        print(f"✗ Configuration file not found at {CONFIG_FILE}")
        print("Please run: python chatgpt2md.py --setup")
        exit(1)

    config = json.loads(CONFIG_FILE.read_text(encoding='utf-8'))

    if not config.get("deepseek_api_key"):
        print("✗ DeepSeek API key not configured")
        print("Please run: python chatgpt2md.py --setup")
        exit(1)

    return config


def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration has required fields."""
    required_fields = ["deepseek_api_key", "output_dir", "model"]
    return all(field in config for field in required_fields)
```

**Step 2: Test manually**

Run: `python -c "from config_manager import create_default_config; print(create_default_config())"`
Expected: See default config dict

**Step 3: Commit**

```bash
git add config_manager.py
git commit -m "feat: add config manager with setup and validation"
```

---

## Task 3: Prompt Template Module

**Files:**
- Modify: `prompt_template.py`

**Step 1: Write prompt template**

```python
"""Prompt template for DeepSeek API structurization."""

SYSTEM_PROMPT = """你是一个专业的知识文档编辑器。

输入：ChatGPT 对话的原始文本
输出：结构化的 Markdown 文档

要求：
1. 识别对话主题，生成简洁的文档标题
2. 提取技术标签（如 [Python, API, Web]），限制在 3-5 个标签
3. 写一段摘要（2-3 句话概括核心内容）
4. 将对话重组为知识章节，使用合理的标题层级（## 和 ###）
5. 过滤无用的对话废话（"好的"、"让我想想"、"谢谢"等）
6. 提取代码块单独呈现在"代码示例"章节
7. 不要保留对话轮次格式（User/Assistant），重组为流畅的说明性内容
8. 识别关键主题，列为项目符号列表

输出格式（严格遵循）：
---
技术标签: [标签1, 标签2, 标签3]
日期: YYYY-MM-DD
来源: [原始URL或文件名]
---

# 文档标题

## 摘要
[2-3 句话概括核心内容]

## 关键主题
- 主题 1
- 主题 2
- 主题 3

## [知识点章节标题 1]
[重组后的说明性内容，非对话格式]

### [子章节标题]
[详细内容]

## [知识点章节标题 2]
[内容...]

## 代码示例
```语言
# 提取的完整代码，带注释说明
```

注意：
- 标题要具体且有信息量，避免"介绍"、"概述"等泛泛标题
- 内容要连贯流畅，像教程或文档而非聊天记录
- 代码示例要完整可运行，添加必要注释
"""


def get_system_prompt() -> str:
    """Get the system prompt for structurization."""
    return SYSTEM_PROMPT
```

**Step 2: Verify prompt loading**

Run: `python -c "from prompt_template import get_system_prompt; print(len(get_system_prompt()))"`
Expected: See character count > 500

**Step 3: Commit**

```bash
git add prompt_template.py
git commit -m "feat: add DeepSeek structurization prompt template"
```

---

## Task 4: Playwright Extractor

**Files:**
- Modify: `extractors/playwright_extractor.py`

**Step 1: Write Playwright extractor**

```python
"""Extract content from ChatGPT share URLs using Playwright."""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def extract_from_url(url: str, timeout: int = 30000) -> str:
    """
    Extract text content from ChatGPT share URL.

    Args:
        url: ChatGPT share URL (e.g., https://chatgpt.com/share/...)
        timeout: Page load timeout in milliseconds

    Returns:
        Extracted plain text content

    Raises:
        PlaywrightTimeoutError: If page fails to load
        ValueError: If URL is invalid
    """
    if not url.startswith('http'):
        raise ValueError(f"Invalid URL: {url}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Navigate and wait for network idle
            page.goto(url, wait_until='networkidle', timeout=timeout)

            # Wait for conversation content to load
            # ChatGPT share pages typically have conversation in main content area
            page.wait_for_selector('main', timeout=10000)

            # Extract plain text from body
            content = page.inner_text('body')

            browser.close()

            return content.strip()

    except PlaywrightTimeoutError as e:
        raise PlaywrightTimeoutError(
            f"Failed to load page within {timeout}ms. "
            "Check your network connection and URL validity."
        ) from e


if __name__ == "__main__":
    # Manual test
    import sys
    if len(sys.argv) > 1:
        url = sys.argv[1]
        print(f"Extracting from: {url}")
        content = extract_from_url(url)
        print(f"Extracted {len(content)} characters")
        print(content[:500])
```

**Step 2: Commit**

```bash
git add extractors/playwright_extractor.py
git commit -m "feat: add Playwright URL extractor with timeout handling"
```

---

## Task 5: Webarchive Extractor

**Files:**
- Modify: `extractors/webarchive_extractor.py`

**Step 1: Write webarchive extractor with HTML parser**

```python
"""Extract content from Safari .webarchive files."""

import plistlib
from pathlib import Path
from html.parser import HTMLParser
from typing import List


class CleanHTMLParser(HTMLParser):
    """HTML parser that extracts clean text, skipping scripts and styles."""

    def __init__(self):
        super().__init__()
        self.text_chunks: List[str] = []
        self.skip_tags = {'script', 'style', 'noscript'}
        self.current_tag = None

    def handle_starttag(self, tag, attrs):
        if tag in self.skip_tags:
            self.current_tag = tag

    def handle_endtag(self, tag):
        if tag == self.current_tag:
            self.current_tag = None

    def handle_data(self, data):
        if self.current_tag is None:
            # Clean whitespace but preserve structure
            cleaned = data.strip()
            if cleaned:
                self.text_chunks.append(cleaned)

    def get_text(self) -> str:
        """Get extracted text with normalized spacing."""
        return '\n'.join(self.text_chunks)


def extract_from_webarchive(filepath: str) -> str:
    """
    Extract text content from Safari .webarchive file.

    Args:
        filepath: Path to .webarchive file

    Returns:
        Extracted plain text content

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not a valid webarchive
    """
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    if path.suffix.lower() != '.webarchive':
        raise ValueError(f"Not a webarchive file: {filepath}")

    try:
        with open(filepath, 'rb') as f:
            plist = plistlib.load(f)

        # Extract main resource HTML data
        if 'WebMainResource' not in plist:
            raise ValueError("Invalid webarchive: missing WebMainResource")

        main_resource = plist['WebMainResource']

        if 'WebResourceData' not in main_resource:
            raise ValueError("Invalid webarchive: missing WebResourceData")

        html_data = main_resource['WebResourceData']

        # Decode HTML (try UTF-8, fallback to latin-1)
        try:
            html = html_data.decode('utf-8')
        except UnicodeDecodeError:
            html = html_data.decode('latin-1', errors='ignore')

        # Parse and clean HTML
        parser = CleanHTMLParser()
        parser.feed(html)

        return parser.get_text()

    except plistlib.InvalidFileException as e:
        raise ValueError(f"Invalid webarchive format: {e}") from e


if __name__ == "__main__":
    # Manual test
    import sys
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        print(f"Extracting from: {filepath}")
        content = extract_from_webarchive(filepath)
        print(f"Extracted {len(content)} characters")
        print(content[:500])
```

**Step 2: Test with existing webarchive**

Run: `python extractors/webarchive_extractor.py "Claude Code 竞争力分析.webarchive"`
Expected: See extracted text preview

**Step 3: Commit**

```bash
git add extractors/webarchive_extractor.py
git commit -m "feat: add webarchive extractor with HTML cleaning"
```

---

## Task 6: AI Structurizer Module

**Files:**
- Modify: `structurizer.py`

**Step 1: Write structurizer with error handling**

```python
"""AI structurization using DeepSeek API."""

import requests
from datetime import datetime
from typing import Dict, Any
from prompt_template import get_system_prompt


def structurize_content(
    raw_text: str,
    config: Dict[str, Any],
    source: str = ""
) -> str:
    """
    Structurize raw text into Markdown using DeepSeek API.

    Args:
        raw_text: Raw extracted text from ChatGPT conversation
        config: Configuration dict with API credentials
        source: Original source URL or filename

    Returns:
        Structured Markdown content

    Raises:
        requests.exceptions.HTTPError: If API call fails
        ValueError: If response is invalid
    """
    api_url = 'https://api.deepseek.com/v1/chat/completions'

    headers = {
        'Authorization': f'Bearer {config["deepseek_api_key"]}',
        'Content-Type': 'application/json'
    }

    # Build system prompt with source info
    system_prompt = get_system_prompt()
    if source:
        system_prompt += f"\n\n原始来源: {source}"

    payload = {
        'model': config.get('model', 'deepseek-chat'),
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': raw_text}
        ],
        'max_tokens': config.get('max_tokens', 4000),
        'temperature': config.get('temperature', 0.7)
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()

        result = response.json()

        if 'choices' not in result or len(result['choices']) == 0:
            raise ValueError("Invalid API response: missing choices")

        markdown = result['choices'][0]['message']['content']

        # Ensure front matter has date and source
        if not markdown.startswith('---'):
            # Add front matter if missing
            today = datetime.now().strftime('%Y-%m-%d')
            front_matter = f"""---
技术标签: []
日期: {today}
来源: {source or 'Unknown'}
---

"""
            markdown = front_matter + markdown

        return markdown

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise requests.exceptions.HTTPError(
                "API authentication failed. Check your API key in config.json"
            ) from e
        elif e.response.status_code == 429:
            raise requests.exceptions.HTTPError(
                "Rate limit exceeded. Please wait and try again."
            ) from e
        else:
            raise requests.exceptions.HTTPError(
                f"API request failed: {e.response.status_code} - {e.response.text}"
            ) from e

    except requests.exceptions.Timeout:
        raise TimeoutError(
            "API request timed out. The conversation might be too long."
        )


if __name__ == "__main__":
    # Manual test with mock config
    import sys
    if len(sys.argv) > 1:
        config = {
            "deepseek_api_key": "your-key-here",
            "model": "deepseek-chat",
            "max_tokens": 4000,
            "temperature": 0.7
        }
        test_text = sys.argv[1]
        result = structurize_content(test_text, config)
        print(result)
```

**Step 2: Commit**

```bash
git add structurizer.py
git commit -m "feat: add DeepSeek API structurizer with error handling"
```

---

## Task 7: Main CLI Script

**Files:**
- Modify: `chatgpt2md.py`

**Step 1: Write main CLI logic**

```python
#!/usr/bin/env python3
"""
ChatGPT2MD - Convert ChatGPT share links to structured Markdown.

Usage:
    python chatgpt2md.py --setup                    # Initial configuration
    python chatgpt2md.py <url>                      # Extract from URL
    python chatgpt2md.py <file.webarchive>          # Extract from webarchive
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Tuple

from config_manager import setup_config, load_config
from extractors.playwright_extractor import extract_from_url
from extractors.webarchive_extractor import extract_from_webarchive
from structurizer import structurize_content


def sanitize_filename(title: str, max_length: int = 50) -> str:
    """
    Sanitize title for use as filename.

    Args:
        title: Original title
        max_length: Maximum length of filename

    Returns:
        Sanitized filename
    """
    # Remove or replace invalid filename characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        title = title.replace(char, '-')

    # Truncate to max length
    if len(title) > max_length:
        title = title[:max_length]

    # Remove leading/trailing spaces and dots
    title = title.strip('. ')

    return title


def generate_filename_from_markdown(markdown: str) -> str:
    """
    Extract title from markdown and generate filename.

    Args:
        markdown: Structured markdown content

    Returns:
        Filename in format: YYYY-MM-DD-title.md
    """
    # Extract first # heading as title
    lines = markdown.split('\n')
    title = "untitled"

    for line in lines:
        line = line.strip()
        if line.startswith('# '):
            title = line[2:].strip()
            break

    # Sanitize and format
    title_clean = sanitize_filename(title)
    today = datetime.now().strftime('%Y-%m-%d')

    return f"{today}-{title_clean}.md"


def extract_content(input_path: str) -> Tuple[str, str]:
    """
    Extract content from URL or webarchive file.

    Args:
        input_path: URL or file path

    Returns:
        Tuple of (extracted_text, source_identifier)
    """
    if input_path.startswith('http'):
        print(f"📡 Extracting from URL: {input_path}")
        text = extract_from_url(input_path)
        source = input_path
    else:
        print(f"📄 Extracting from webarchive: {input_path}")
        text = extract_from_webarchive(input_path)
        source = Path(input_path).name

    print(f"✓ Extracted {len(text)} characters")
    return text, source


def determine_output_path(input_path: str, markdown: str, config: dict) -> Path:
    """
    Determine output path based on input type.

    Args:
        input_path: Original input (URL or file path)
        markdown: Generated markdown (for title extraction)
        config: Configuration dict

    Returns:
        Output file path
    """
    if input_path.startswith('http'):
        # URL input: use config output_dir
        output_dir = Path(config['output_dir']).expanduser()
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = generate_filename_from_markdown(markdown)
        output_path = output_dir / filename
    else:
        # Webarchive input: same directory as input file
        input_file = Path(input_path)
        output_path = input_file.with_suffix('.md')

    # Handle filename conflicts
    if output_path.exists():
        base = output_path.stem
        suffix = output_path.suffix
        parent = output_path.parent
        counter = 1
        while output_path.exists():
            output_path = parent / f"{base}-{counter}{suffix}"
            counter += 1

    return output_path


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Convert ChatGPT conversations to structured Markdown',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python chatgpt2md.py --setup
  python chatgpt2md.py https://chatgpt.com/share/xxx
  python chatgpt2md.py ~/Downloads/chat.webarchive
        """
    )

    parser.add_argument(
        'input',
        nargs='?',
        help='ChatGPT share URL or .webarchive file path'
    )

    parser.add_argument(
        '--setup',
        action='store_true',
        help='Initialize configuration (API key, output directory, etc.)'
    )

    args = parser.parse_args()

    # Handle setup mode
    if args.setup:
        setup_config()
        return

    # Validate input
    if not args.input:
        parser.print_help()
        print("\n✗ Error: Please provide a URL or file path")
        sys.exit(1)

    try:
        # Load configuration
        config = load_config()

        # Extract content
        raw_text, source = extract_content(args.input)

        # Structurize with AI
        print("🤖 Structurizing with DeepSeek API...")
        markdown = structurize_content(raw_text, config, source)

        # Determine output path
        output_path = determine_output_path(args.input, markdown, config)

        # Save to file
        output_path.write_text(markdown, encoding='utf-8')

        print(f"✓ Saved to: {output_path}")

    except FileNotFoundError as e:
        print(f"✗ File error: {e}")
        sys.exit(1)

    except ValueError as e:
        print(f"✗ Validation error: {e}")
        sys.exit(1)

    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

**Step 2: Make script executable**

Run: `chmod +x chatgpt2md.py`

**Step 3: Test help output**

Run: `python chatgpt2md.py --help`
Expected: See usage help

**Step 4: Commit**

```bash
git add chatgpt2md.py
git commit -m "feat: add main CLI script with input routing and error handling"
```

---

## Task 8: Add extractors __init__.py

**Files:**
- Modify: `extractors/__init__.py`

**Step 1: Write package init**

```python
"""Content extractors for ChatGPT2MD."""

from .playwright_extractor import extract_from_url
from .webarchive_extractor import extract_from_webarchive

__all__ = ['extract_from_url', 'extract_from_webarchive']
```

**Step 2: Commit**

```bash
git add extractors/__init__.py
git commit -m "feat: add extractors package exports"
```

---

## Task 9: Create README with Usage Instructions

**Files:**
- Create: `README.md`

**Step 1: Write comprehensive README**

```markdown
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
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add comprehensive README with installation and usage"
```

---

## Task 10: Add .gitignore

**Files:**
- Create: `.gitignore`

**Step 1: Write .gitignore**

```
# Config with API keys
config.json

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/

# Output
output/
*.md
!README.md
!docs/**/*.md

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Test files
*.webarchive
extracted_*.txt
extracted_*.html
```

**Step 2: Commit**

```bash
git add .gitignore
git commit -m "chore: add .gitignore for config and output files"
```

---

## Task 11: Integration Test with Existing Webarchive

**Files:**
- Test: Run full pipeline with existing file

**Step 1: Run setup**

Run: `python chatgpt2md.py --setup`
Expected: Prompt for API key and output dir
Action: Enter valid DeepSeek API key

**Step 2: Test webarchive extraction**

Run: `python chatgpt2md.py "Claude Code 竞争力分析.webarchive"`
Expected:
- See extraction progress messages
- API call to DeepSeek
- Output file created: `Claude Code 竞争力分析.md`

**Step 3: Verify output file**

Run: `head -50 "Claude Code 竞争力分析.md"`
Expected: See structured Markdown with front matter, title, summary, sections

**Step 4: Commit test result**

```bash
git add config.json
git commit -m "test: verify full pipeline with existing webarchive"
```

---

## Task 12: Final Verification and Documentation

**Files:**
- Verify: All components working together

**Step 1: Verify project structure**

Run: `tree -I '__pycache__|*.pyc'`
Expected: See complete project structure

**Step 2: Verify all imports**

Run: `python -c "import chatgpt2md; import config_manager; import structurizer; import prompt_template; from extractors import extract_from_url, extract_from_webarchive"`
Expected: No import errors

**Step 3: Run help command**

Run: `python chatgpt2md.py --help`
Expected: Clean, informative help output

**Step 4: Final commit**

```bash
git add -A
git commit -m "chore: final verification and cleanup"
```

---

## Success Criteria

- ✅ Clean project structure with modular components
- ✅ Config setup workflow functional
- ✅ Playwright extraction works with ChatGPT URLs
- ✅ Webarchive extraction works with Safari files
- ✅ DeepSeek API integration with error handling
- ✅ Output paths handled correctly (URL vs file input)
- ✅ Structured Markdown output with proper formatting
- ✅ Comprehensive error messages for common issues
- ✅ README with clear installation and usage instructions

## Notes

- Test with actual ChatGPT share URL requires valid URL (user should provide)
- DeepSeek API key required for structurization step
- Playwright may take 30-60s for first run (browser download)
- Token usage typically 2000-3000 tokens per conversation
