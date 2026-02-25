"""Extract content from HTML files (.html, .mhtml, etc.)."""

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


def extract_from_html(filepath: str) -> str:
    """
    Extract text content from HTML file.

    Args:
        filepath: Path to HTML file (.html, .mhtml, etc.)

    Returns:
        Extracted plain text content

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not a valid HTML file
    """
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    # Accept .html and .mhtml files
    suffix = path.suffix.lower()
    if suffix not in ['.html', '.htm', '.mhtml', '.xhtml']:
        raise ValueError(f"Not a supported HTML file: {filepath}")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            html = f.read()

        # Parse and clean HTML
        parser = CleanHTMLParser()
        parser.feed(html)

        return parser.get_text()

    except UnicodeDecodeError:
        # Try different encoding
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                html = f.read()
            parser = CleanHTMLParser()
            parser.feed(html)
            return parser.get_text()
        except Exception as e:
            raise ValueError(f"Could not decode HTML file: {e}") from e


if __name__ == "__main__":
    # Manual test
    import sys
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        print(f"Extracting from: {filepath}")
        content = extract_from_html(filepath)
        print(f"Extracted {len(content)} characters")
        print(content[:500])
