"""AI structurization using OpenAI-compatible APIs."""

import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


def load_system_prompt(language: str) -> str:
    """
    Load system prompt for the specified language.

    Args:
        language: Language code ('en' or 'zh')

    Returns:
        System prompt text

    Raises:
        FileNotFoundError: If prompt file doesn't exist
    """
    prompt_file = Path(__file__).parent / "prompts" / f"system_prompt_{language}.txt"

    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

    return prompt_file.read_text(encoding='utf-8')


def structurize_content(
    raw_text: str,
    config: Dict[str, Any],
    source: str = ""
) -> str:
    """
    Structurize raw text into Markdown using OpenAI-compatible API.

    Args:
        raw_text: Raw extracted text from AI conversation
        config: Configuration dict with API credentials
        source: Original source URL or filename

    Returns:
        Structured Markdown content

    Raises:
        requests.exceptions.HTTPError: If API call fails
        ValueError: If response is invalid
    """
    # Load system prompt based on language
    language = config.get("language", "en")
    system_prompt = load_system_prompt(language)

    # Append source info to prompt if available
    if source:
        if language == "zh":
            system_prompt += f"\n\n原始来源: {source}"
        else:
            system_prompt += f"\n\nOriginal source: {source}"

    # Construct API URL (ensure /v1/chat/completions endpoint)
    api_base = config["api_base_url"].rstrip('/')
    if not api_base.endswith('/v1'):
        api_url = f"{api_base}/v1/chat/completions"
    else:
        api_url = f"{api_base}/chat/completions"

    headers = {
        'Authorization': f'Bearer {config["api_key"]}',
        'Content-Type': 'application/json'
    }

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

        # Ensure front matter has date and source if not already present
        if not markdown.startswith('---'):
            # Add front matter if missing
            today = datetime.now().strftime('%Y-%m-%d')
            if language == "zh":
                front_matter = f"""---
技术标签: []
日期: {today}
来源: {source or 'Unknown'}
---

"""
            else:
                front_matter = f"""---
tags: []
date: {today}
source: {source or 'Unknown'}
---

"""
            markdown = front_matter + markdown

        return markdown

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise requests.exceptions.HTTPError(
                "API authentication failed. Check your API key"
            ) from e
        elif e.response.status_code == 429:
            raise requests.exceptions.HTTPError(
                "Rate limit exceeded. Please wait and try again"
            ) from e
        else:
            error_msg = f"API request failed: {e.response.status_code}"
            try:
                error_detail = e.response.json()
                error_msg += f" - {error_detail}"
            except:
                error_msg += f" - {e.response.text[:200]}"
            raise requests.exceptions.HTTPError(error_msg) from e

    except requests.exceptions.Timeout:
        raise TimeoutError(
            "API request timed out. The conversation might be too long"
        )

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Network error: {e}") from e
