#!/usr/bin/env python3
"""
aichat2md - Convert AI chat conversations to structured Markdown.

Usage:
    aichat2md --setup                    # Initial configuration
    aichat2md <url>                      # Extract from URL
    aichat2md <file.webarchive>          # Extract from webarchive
    aichat2md <url> --lang zh            # Override language
    aichat2md <url> -o output.md         # Custom output path
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Tuple
import time

from yaspin import yaspin

from .config import setup_config, load_config
from .extractors.playwright_extractor import extract_from_url
from .extractors.webarchive_extractor import extract_from_webarchive
from .structurizer import structurize_content
from . import __version__


class TimedText:
    """Dynamic text with elapsed time in seconds."""
    def __init__(self, text: str):
        self.text = text
        self._start = time.time()

    def __str__(self):
        elapsed = int(time.time() - self._start)
        return f"[{elapsed}s] {self.text}"


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
        with yaspin(text=TimedText(f"Extracting from URL (up to 60s): {input_path}")) as sp:
            text = extract_from_url(input_path)
            sp.ok(f"✓ Extracted {len(text)} characters")
        source = input_path
    else:
        # Webarchive extraction is fast, no spinner needed
        print(f"📄 Extracting from webarchive: {input_path}")
        text = extract_from_webarchive(input_path)
        print(f"✓ Extracted {len(text)} characters")
        source = Path(input_path).name

    return text, source


def determine_output_path(input_path: str, markdown: str, config: dict, custom_output: str = None) -> Path:
    """
    Determine output path based on input type and custom override.

    Args:
        input_path: Original input (URL or file path)
        markdown: Generated markdown (for title extraction)
        config: Configuration dict
        custom_output: Custom output path from CLI argument

    Returns:
        Output file path
    """
    if custom_output:
        # Use custom output path
        output_path = Path(custom_output).expanduser()
        # Ensure .md extension
        if not output_path.suffix:
            output_path = output_path.with_suffix('.md')
    elif input_path.startswith('http'):
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
        prog="aichat2md",
        description='Convert AI chat conversations to structured Markdown',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  aichat2md --setup
  aichat2md https://chatgpt.com/share/xxx
  aichat2md ~/Downloads/chat.webarchive
  aichat2md <url> --lang zh
  aichat2md <url> -o ~/Documents/output.md
  aichat2md <url> --model gpt-4o
        """
    )

    parser.add_argument(
        'input',
        nargs='?',
        help='AI chat share URL or .webarchive file path'
    )

    parser.add_argument(
        '--setup',
        action='store_true',
        help='Initialize configuration (API key, provider, language, etc.)'
    )

    parser.add_argument(
        '--lang',
        choices=['en', 'zh'],
        help='Override prompt language (English or Chinese)'
    )

    parser.add_argument(
        '--output', '-o',
        help='Custom output file path'
    )

    parser.add_argument(
        '--model',
        help='Override AI model'
    )

    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
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

        # Override config with CLI arguments
        if args.lang:
            config["language"] = args.lang
        if args.model:
            config["model"] = args.model

        # Extract content
        raw_text, source = extract_content(args.input)

        # Structurize with AI
        provider = config.get("api_base_url", "API")
        estimated = min(60 + len(raw_text) // 100, 600)
        with yaspin(text=TimedText(f"Structurizing {len(raw_text)} chars with {provider} (~{estimated}s)")) as sp:
            markdown = structurize_content(raw_text, config, source)
            sp.ok("✓ Structurized")

        # Determine output path
        output_path = determine_output_path(args.input, markdown, config, args.output)

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

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
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
