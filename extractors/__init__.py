"""Content extractors for ChatGPT2MD."""

from .playwright_extractor import extract_from_url
from .webarchive_extractor import extract_from_webarchive

__all__ = ['extract_from_url', 'extract_from_webarchive']
