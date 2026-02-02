"""AI structurization using DeepSeek API."""

import requests
from datetime import datetime
from typing import Dict, Any
from prompt_template import get_system_prompt


def structurize_content(
    raw_text: str,
    config: Dict[str, Any],
    source: str = ""
) -> str:
    """
    Structurize raw text into Markdown using DeepSeek API.

    Args:
        raw_text: Raw extracted text from ChatGPT conversation
        config: Configuration dict with API credentials
        source: Original source URL or filename

    Returns:
        Structured Markdown content

    Raises:
        requests.exceptions.HTTPError: If API call fails
        ValueError: If response is invalid
    """
    api_url = 'https://api.deepseek.com/v1/chat/completions'

    headers = {
        'Authorization': f'Bearer {config["deepseek_api_key"]}',
        'Content-Type': 'application/json'
    }

    # Build system prompt with source info
    system_prompt = get_system_prompt()
    if source:
        system_prompt += f"\n\n原始来源: {source}"

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

        # Ensure front matter has date and source
        if not markdown.startswith('---'):
            # Add front matter if missing
            today = datetime.now().strftime('%Y-%m-%d')
            front_matter = f"""---
技术标签: []
日期: {today}
来源: {source or 'Unknown'}
---

"""
            markdown = front_matter + markdown

        return markdown

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise requests.exceptions.HTTPError(
                "API authentication failed. Check your API key in config.json"
            ) from e
        elif e.response.status_code == 429:
            raise requests.exceptions.HTTPError(
                "Rate limit exceeded. Please wait and try again."
            ) from e
        else:
            raise requests.exceptions.HTTPError(
                f"API request failed: {e.response.status_code} - {e.response.text}"
            ) from e

    except requests.exceptions.Timeout:
        raise TimeoutError(
            "API request timed out. The conversation might be too long."
        )


if __name__ == "__main__":
    # Manual test with mock config
    import sys
    if len(sys.argv) > 1:
        config = {
            "deepseek_api_key": "your-key-here",
            "model": "deepseek-chat",
            "max_tokens": 4000,
            "temperature": 0.7
        }
        test_text = sys.argv[1]
        result = structurize_content(test_text, config)
        print(result)
