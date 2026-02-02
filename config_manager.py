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
