"""Tests for configuration management."""

import pytest
from aichat2md.config import validate_config, API_PRESETS, DEFAULT_CONFIG


def test_default_config_structure():
    """Test default config has all required fields."""
    required_fields = ["api_key", "api_base_url", "model", "output_dir", "language"]
    for field in required_fields:
        assert field in DEFAULT_CONFIG


def test_validate_config_success():
    """Test config validation with valid config."""
    config = {
        "api_key": "sk-test-key",
        "api_base_url": "https://api.example.com",
        "model": "test-model",
        "output_dir": "/tmp"
    }
    assert validate_config(config) is True


def test_validate_config_missing_fields():
    """Test config validation fails with missing fields."""
    config = {"api_key": "sk-test"}
    assert validate_config(config) is False


def test_api_presets_structure():
    """Test API presets have required structure."""
    for name, preset in API_PRESETS.items():
        assert "api_base_url" in preset
        assert "model" in preset
        assert "description" in preset


def test_deepseek_preset():
    """Test DeepSeek preset configuration."""
    preset = API_PRESETS["deepseek"]
    assert "deepseek.com" in preset["api_base_url"]
    assert preset["model"] == "deepseek-chat"


def test_openai_preset():
    """Test OpenAI preset configuration."""
    preset = API_PRESETS["openai"]
    assert "openai.com" in preset["api_base_url"]
    assert "gpt" in preset["model"].lower()
