#!/usr/bin/env python3
"""
Debug script to discover Claude share page cookies.
Uses headless mode with stealth settings.
"""

from playwright.sync_api import sync_playwright
import json


def discover_cookies(url: str, headless: bool = True):
    """Discover cookies set by Claude share page after consent."""

    print(f"\n{'='*60}")
    print("Claude Cookie Discovery Tool")
    print(f"{'='*60}")
    print(f"\nTarget URL: {url}")
    print(f"Headless: {headless}")

    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
            ]
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
        )
        page = context.new_page()

        # Stealth scripts
        page.add_init_script('Object.defineProperty(navigator, "webdriver", {get: () => undefined})')
        page.add_init_script('Object.defineProperty(navigator, "plugins", {get: () => [1, 2, 3, 4, 5]})')
        page.add_init_script('Object.defineProperty(navigator, "languages", {get: () => ["en-US", "en"]})')
        page.add_init_script('window.chrome = {runtime: {}}')

        # Get cookies BEFORE navigation
        print("\n--- Cookies BEFORE navigation ---")
        cookies_before = context.cookies()
        print(f"Count: {len(cookies_before)}")

        # Navigate to the page
        print("\n--- Navigating to page ---")
        try:
            response = page.goto(url, wait_until='domcontentloaded', timeout=60000)
            if response:
                print(f"Status: {response.status}")
                print(f"Final URL: {response.url}")

                # Check for region block
                if "unavailable" in response.url.lower():
                    print("\n!!! REGION BLOCK DETECTED !!!")
                    print("Claude is redirecting to 'app-unavailable-in-region'")
                    print("\nPossible solutions:")
                    print("1. Use a VPN in a supported region (US, UK, etc.)")
                    print("2. The share link may be region-locked")
                    browser.close()
                    return []
        except Exception as e:
            print(f"Navigation error: {e}")

        # Wait for page to settle
        print("\n--- Waiting for page to load ---")
        try:
            page.wait_for_timeout(5000)
        except Exception as e:
            print(f"Wait error: {e}")
            browser.close()
            return []

        # Check current URL
        try:
            current_url = page.url()
            print(f"Current URL: {current_url}")
            if "unavailable" in current_url.lower():
                print("\n!!! REGION BLOCK !!!")
                browser.close()
                return []
        except:
            pass

        # Get cookies after load
        print("\n--- Cookies after page load ---")
        cookies_after_load = context.cookies()
        print(f"Count: {len(cookies_after_load)}")
        for cookie in cookies_after_load:
            val = cookie['value'][:80] + '...' if len(cookie['value']) > 80 else cookie['value']
            print(f"  {cookie['name']}: {val}")

        # Take screenshot before consent
        try:
            page.screenshot(path='/tmp/claude_before_consent.png', full_page=True)
            print("\nScreenshot before: /tmp/claude_before_consent.png")
        except:
            pass

        # Click "Accept All Cookies" button
        print("\n--- Attempting to bypass consent ---")

        # Method 1: Try setting localStorage/sessionStorage first
        print("Method 1: Setting localStorage consent flags...")
        try:
            # Common consent storage keys
            consent_keys = [
                ('localStorage', 'cookieConsent', 'true'),
                ('localStorage', 'cookie-consent', 'true'),
                ('localStorage', 'consent', 'accepted'),
                ('localStorage', 'anthropic-consent', 'true'),
                ('localStorage', 'functionalConsent', 'true'),
                ('localStorage', 'analyticsConsent', 'true'),
                ('sessionStorage', 'cookieConsent', 'true'),
            ]
            for storage, key, value in consent_keys:
                page.evaluate(f"window.{storage}.setItem('{key}', '{value}')")
            print("Set consent flags in storage")
        except Exception as e:
            print(f"Storage error: {e}")

        # Method 2: Remove consent banner from DOM
        print("\nMethod 2: Removing consent banner from DOM...")
        try:
            # Try to find and remove the banner
            removed = page.evaluate('''() => {
                // Find common consent banner selectors
                const selectors = [
                    '[class*="cookie"]',
                    '[class*="consent"]',
                    '[class*="banner"]',
                    '[id*="cookie"]',
                    '[id*="consent"]',
                    '[data-testid*="cookie"]',
                    '[data-testid*="consent"]',
                    'div[role="dialog"]',
                ];
                let removed = 0;
                for (const sel of selectors) {
                    const elements = document.querySelectorAll(sel);
                    elements.forEach(el => {
                        if (el.innerText && (
                            el.innerText.toLowerCase().includes('cookie') ||
                            el.innerText.toLowerCase().includes('consent')
                        )) {
                            el.remove();
                            removed++;
                        }
                    });
                }
                return removed;
            }''')
            print(f"Removed {removed} potential banner elements")
        except Exception as e:
            print(f"Remove error: {e}")

        # Method 3: Dispatch consent event
        print("\nMethod 3: Dispatching consent events...")
        try:
            page.evaluate('''() => {
                // Try to dispatch consent events
                window.dispatchEvent(new CustomEvent('consent', { detail: { accepted: true } }));
                window.dispatchEvent(new CustomEvent('cookieConsent', { detail: { accepted: true } }));
                document.dispatchEvent(new CustomEvent('consent', { detail: { accepted: true } }));
            }''')
            print("Dispatched consent events")
        except Exception as e:
            print(f"Event error: {e}")

        # Wait and check content
        page.wait_for_timeout(2000)

        # Method 4: Try clicking with JavaScript
        print("\nMethod 4: JavaScript click on Accept button...")
        try:
            clicked = page.evaluate('''() => {
                const buttons = document.querySelectorAll('button');
                for (const btn of buttons) {
                    if (btn.innerText.includes('Accept All Cookies') ||
                        btn.innerText.includes('Accept All')) {
                        btn.click();
                        return btn.innerText;
                    }
                }
                return null;
            }''')
            if clicked:
                print(f"JS clicked: {clicked}")
            else:
                print("No button found via JS")
        except Exception as e:
            print(f"JS click error: {e}")

        page.wait_for_timeout(2000)

        # Get cookies AFTER consent
        print("\n--- Cookies AFTER consent ---")
        cookies_after_consent = context.cookies()
        print(f"Count: {len(cookies_after_consent)}")

        # Find NEW cookies
        before_names = {c['name'] for c in cookies_after_load}
        new_cookies = [c for c in cookies_after_consent if c['name'] not in before_names]

        if new_cookies:
            print(f"\n=== NEW COOKIES (the ones we need) ===")
            for cookie in new_cookies:
                print(f"\n  Name: {cookie['name']}")
                print(f"  Value: {cookie['value']}")
                print(f"  Domain: {cookie.get('domain')}")
                print(f"  Path: {cookie.get('path')}")
        else:
            print("\nNo new cookies detected. All cookies:")
            for cookie in cookies_after_consent:
                print(f"  {cookie['name']}: {cookie['value'][:80]}")

        # Take screenshot after consent
        try:
            page.screenshot(path='/tmp/claude_after_consent.png', full_page=True)
            print("\nScreenshot after: /tmp/claude_after_consent.png")
        except:
            pass

        # Get page content AFTER consent
        print("\n--- Page content AFTER consent ---")
        try:
            content = page.content()
            text = page.inner_text('body')
            print(f"HTML length: {len(content)} chars")
            print(f"Text length: {len(text)} chars")
            print(f"Preview:\n{text[:800]}...")
        except Exception as e:
            print(f"Content error: {e}")

        # Save cookies
        with open('/tmp/claude_cookies.json', 'w') as f:
            json.dump({
                'before_consent': cookies_after_load,
                'after_consent': cookies_after_consent,
                'new_cookies': new_cookies
            }, f, indent=2)
        print("\nCookies saved: /tmp/claude_cookies.json")

        browser.close()
        return new_cookies


if __name__ == "__main__":
    import sys
    test_url = sys.argv[1] if len(sys.argv) > 1 else None
    if not test_url:
        print("Usage: python debug_claude_cookies.py <claude_share_url>")
        sys.exit(1)
    discover_cookies(test_url)
