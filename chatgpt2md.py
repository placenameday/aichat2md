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
