"""Extract content from ChatGPT share URLs using Playwright."""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def extract_from_url(url: str, timeout: int = 30000) -> str:
    """
    Extract text content from ChatGPT share URL.

    Args:
        url: ChatGPT share URL (e.g., https://chatgpt.com/share/...)
        timeout: Page load timeout in milliseconds

    Returns:
        Extracted plain text content

    Raises:
        PlaywrightTimeoutError: If page fails to load
        ValueError: If URL is invalid
    """
    if not url.startswith('http'):
        raise ValueError(f"Invalid URL: {url}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Navigate and wait for network idle
            page.goto(url, wait_until='networkidle', timeout=timeout)

            # Wait for conversation content to load
            # ChatGPT share pages typically have conversation in main content area
            page.wait_for_selector('main', timeout=10000)

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
