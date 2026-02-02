"""Configuration management for aichat2md."""

import json
from pathlib import Path
from typing import Dict, Any


# Configuration file location (cross-platform)
CONFIG_DIR = Path.home() / ".config" / "aichat2md"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Default configuration
DEFAULT_CONFIG = {
    "api_key": "",
    "api_base_url": "https://api.deepseek.com",
    "language": "en",
    "output_dir": str(Path.home() / "Downloads"),
    "model": "deepseek-chat",
    "max_tokens": 4000,
    "temperature": 0.7
}

# API preset configurations
API_PRESETS = {
    "deepseek": {
        "api_base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "description": "DeepSeek (cost-effective, Chinese service)"
    },
    "openai": {
        "api_base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
        "description": "OpenAI (GPT-4o-mini)"
    },
    "groq": {
        "api_base_url": "https://api.groq.com/openai/v1",
        "model": "llama-3.3-70b-versatile",
        "description": "Groq (fast inference)"
    },
    "custom": {
        "api_base_url": "",
        "model": "",
        "description": "Custom OpenAI-compatible API"
    }
}


def get_default_output_dir() -> str:
    """Get platform-specific default downloads directory."""
    return str(Path.home() / "Downloads")


def setup_config():
    """Interactive config setup with API provider selection."""
    print("=== aichat2md Configuration Setup ===\n")

    # Step 1: Select API provider
    print("Select API provider:")
    for i, (key, preset) in enumerate(API_PRESETS.items(), 1):
        print(f"{i}. {preset['description']}")

    while True:
        choice = input(f"\nChoice (1-{len(API_PRESETS)}) [1]: ").strip() or "1"
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(API_PRESETS):
                break
        except ValueError:
            pass
        print("Invalid choice, please try again")

    provider_key = list(API_PRESETS.keys())[choice_idx]
    preset = API_PRESETS[provider_key]

    # Step 2: API configuration
    api_key = input(f"\nEnter your {provider_key.upper()} API key: ").strip()

    if provider_key == "custom":
        api_base_url = input("Enter API base URL (e.g., http://localhost:8000): ").strip()
        model = input("Enter model name: ").strip()
    else:
        api_base_url = preset["api_base_url"]
        model = preset["model"]
        print(f"Using: {api_base_url}")
        print(f"Model: {model}")

    # Step 3: Language selection
    print("\nSelect language for AI prompts:")
    print("1. English")
    print("2. 中文 (Chinese)")
    lang_choice = input("Choice (1-2) [1]: ").strip() or "1"
    language = "zh" if lang_choice == "2" else "en"

    # Step 4: Output directory
    default_dir = get_default_output_dir()
    output_dir = input(f"\nOutput directory (default: {default_dir}): ").strip()
    if not output_dir:
        output_dir = default_dir

    # Create config
    config = DEFAULT_CONFIG.copy()
    config.update({
        "api_key": api_key,
        "api_base_url": api_base_url,
        "model": model,
        "language": language,
        "output_dir": output_dir
    })

    # Save config
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding='utf-8')

    print(f"\n✓ Configuration saved to {CONFIG_FILE}")


def load_config() -> Dict[str, Any]:
    """Load configuration from file."""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Configuration file not found. Please run: aichat2md --setup"
        )

    try:
        config = json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file: {e}")

    if not config.get("api_key"):
        raise ValueError("API key not configured. Please run: aichat2md --setup")

    # Merge with defaults for backward compatibility
    full_config = DEFAULT_CONFIG.copy()
    full_config.update(config)

    return full_config


def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration has required fields."""
    required_fields = ["api_key", "api_base_url", "model", "output_dir"]
    return all(field in config and config[field] for field in required_fields)
