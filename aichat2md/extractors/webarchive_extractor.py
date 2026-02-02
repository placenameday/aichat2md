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
