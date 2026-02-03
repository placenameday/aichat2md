"""Extract content from AI chat share URLs using Playwright."""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def _detect_platform(url: str) -> str:
    """
    Detect platform from URL.

    Args:
        url: Share URL

    Returns:
        Platform name: 'doubao', 'gemini', or 'default'
    """
    url_lower = url.lower()
    if 'doubao.com' in url_lower:
        return 'doubao'
    elif 'gemini.google.com' in url_lower or 'g.co' in url_lower:
        return 'gemini'
    else:
        return 'default'


def _get_wait_time(platform: str) -> int:
    """
    Get wait time in milliseconds for platform.

    Args:
        platform: Platform name from _detect_platform

    Returns:
        Wait time in milliseconds
    """
    wait_times = {
        'doubao': 3000,
        'gemini': 5000,
        'default': 2000
    }
    return wait_times.get(platform, 2000)


def extract_from_url(url: str, timeout: int = 60000) -> str:
    """
    Extract text content from AI chat share URL.

    Args:
        url: Share URL (ChatGPT, Gemini, Doubao, etc.)
        timeout: Page load timeout in milliseconds

    Returns:
        Extracted plain text content

    Raises:
        PlaywrightTimeoutError: If page fails to load
        ValueError: If URL is invalid
    """
    if not url.startswith('http'):
        raise ValueError(f"Invalid URL: {url}")

    # Detect platform and get corresponding wait time
    platform = _detect_platform(url)
    wait_time = _get_wait_time(platform)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Navigate with appropriate wait strategy
            # Use 'load' for Gemini/Doubao (networkidle may timeout due to ongoing requests)
            wait_strategy = 'load' if platform in ['gemini', 'doubao'] else 'networkidle'
            page.goto(url, wait_until=wait_strategy, timeout=60000)

            # Wait for content to load
            # Try to wait for main selector (works for ChatGPT)
            try:
                page.wait_for_selector('main', timeout=10000)
            except PlaywrightTimeoutError:
                # Some platforms may not have 'main' element, continue anyway
                pass

            # Additional wait for dynamic content based on platform
            page.wait_for_timeout(wait_time)

            # Extract plain text from body
            content = page.inner_text('body')

            browser.close()

            return content.strip()

    except PlaywrightTimeoutError as e:
        raise PlaywrightTimeoutError(
            f"Failed to load page within {timeout}ms. "
            "Check your network connection and URL validity."
        ) from e


if __name__ == "__main__":
    # Manual test
    import sys
    if len(sys.argv) > 1:
        url = sys.argv[1]
        print(f"Extracting from: {url}")
        content = extract_from_url(url)
        print(f"Extracted {len(content)} characters")
        print(content[:500])
