"""Tests for CLI interface."""

import pytest
from aichat2md.cli import sanitize_filename, generate_filename_from_markdown


def test_sanitize_filename_basic():
    """Test basic filename sanitization."""
    result = sanitize_filename("Test Title")
    assert result == "Test Title"


def test_sanitize_filename_invalid_chars():
    """Test removal of invalid filename characters."""
    result = sanitize_filename("Test<>:/Title")
    assert "<" not in result
    assert ">" not in result
    assert ":" not in result


def test_sanitize_filename_truncate():
    """Test filename truncation to max length."""
    long_title = "a" * 100
    result = sanitize_filename(long_title, max_length=50)
    assert len(result) == 50


def test_generate_filename_from_markdown():
    """Test filename generation from markdown content."""
    markdown = """---
tags: [test]
---

# Test Document Title

Content here.
"""
    result = generate_filename_from_markdown(markdown)
    assert "Test Document Title" in result
    assert result.endswith(".md")
    assert result.count("-") >= 2  # Date format: YYYY-MM-DD


def test_generate_filename_no_title():
    """Test filename generation when no title found."""
    markdown = "Just some content without a title"
    result = generate_filename_from_markdown(markdown)
    assert "untitled" in result
