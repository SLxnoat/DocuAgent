"""
Authentication handler for DocuAgent AI.
Provides robust form login handling for Playwright automation.
"""

from playwright.async_api import Page


async def handle_login(page: Page, username: str, password: str) -> None:
    """
    Handle form login by finding username/password inputs via robust selector chains
    and submitting the form.

    Args:
        page: Playwright Page object
        username: Username to fill in
        password: Password to fill in

    Raises:
        ValueError: If username or password field cannot be found
    """
    # Define robust selector chains for username field
    username_selectors: list[str] = [
        'input[name="username"]',
        'input[id="username"]',
        'input[type="text"]:not([type="hidden"]):first-of-type',
        'input[placeholder*="username" i]',
        'input[aria-label*="username" i]',
        'input[autocomplete="username"]',
        "#username",
        ".username",
        '[data-testid="username"]',
        '[data-testid="user"]',
        '[data-testid="login-username"]',
    ]

    # Define robust selector chains for password field
    password_selectors: list[str] = [
        'input[name="password"]',
        'input[type="password"]',
        'input[placeholder*="password" i]',
        'input[aria-label*="password" i]',
        'input[autocomplete="current-password"]',
        "#password",
        ".password",
        '[data-testid="password"]',
        '[data-testid="pass"]',
        '[data-testid="login-password"]',
    ]

    # Find and fill username field
    username_filled = False
    for selector in username_selectors:
        try:
            # Wait for the element to be attached and visible
            await page.wait_for_selector(selector, state="attached", timeout=1000)
            # Check if it's an input element and not hidden
            element = await page.query_selector(selector)
            if element:
                # Check if it's visible and enabled
                is_visible = await element.is_visible()
                is_enabled = await element.is_enabled()
                if is_visible and is_enabled:
                    await page.fill(selector, username)
                    username_filled = True
                    break
        except Exception:
            # Try next selector
            continue

    if not username_filled:
        raise ValueError("Could not find or interact with username field")

    # Find and fill password field
    password_filled = False
    for selector in password_selectors:
        try:
            await page.wait_for_selector(selector, state="attached", timeout=1000)
            element = await page.query_selector(selector)
            if element:
                is_visible = await element.is_visible()
                is_enabled = await element.is_enabled()
                if is_visible and is_enabled:
                    await page.fill(selector, password)
                    password_filled = True
                    break
        except Exception:
            continue

    if not password_filled:
        raise ValueError("Could not find or interact with password field")

    # Attempt to submit the form
    # Try to find a submit button first
    submit_selectors: list[str] = [
        'button[type="submit"]',
        'input[type="submit"]',
        'button:has-text("Log in")',
        'button:has-text("Sign in")',
        'button:has-text("Login")',
        'button:has-text("Submit")',
        '[data-testid="submit"]',
        '[data-testid="login-submit"]',
    ]

    submit_clicked = False
    for selector in submit_selectors:
        try:
            await page.wait_for_selector(selector, state="attached", timeout=1000)
            element = await page.query_selector(selector)
            if element:
                is_visible = await element.is_visible()
                is_enabled = await element.is_enabled()
                if is_visible and is_enabled:
                    await page.click(selector)
                    submit_clicked = True
                    break
        except Exception:
            continue

    # If no submit button found, try pressing Enter on the password field
    if not submit_clicked:
        try:
            # Press Enter on the last password selector we tried (or just the password field in general)
            # We'll use the last password selector that we know exists (but we don't store it)
            # Instead, we can press Enter on the active element or just press Enter on the page
            # A common approach is to press Enter on the password field
            # We'll try to press Enter on the password field by focusing it and pressing Enter
            # We'll use the last password selector from our list that we know is present?
            # Instead, we'll just press Enter on the body or use the password field we found.
            # Since we didn't store the successful password selector, we'll try to find it again.
            # Alternatively, we can press Enter on the page (which might submit the form if the password field is focused)
            # But a more reliable way is to press Enter on the password field we just filled.
            # We'll attempt to press Enter on the password field by using the first password selector that we know works?
            # Since we didn't store it, we'll try the first password selector again (which might be fragile).
            # Alternatively, we can press Enter on the active element (which should be the password field after we filled it).
            # However, to be safe, we'll try to press Enter on the password field by using the same selector we used to fill it.
            # We don't have that selector stored, so we'll try to find it again by trying the password selectors until we find one that works.
            for selector in password_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        is_visible = await element.is_visible()
                        is_enabled = await element.is_enabled()
                        if is_visible and is_enabled:
                            await page.focus(selector)
                            await page.keyboard.press("Enter")
                            submit_clicked = True
                            break
                except Exception:
                    continue
        except Exception:
            # If all else fails, we'll try pressing Enter on the body (less reliable)
            await page.keyboard.press("Enter")

    # Wait for a bit to allow navigation or any post-login actions
    # We'll wait for network idle or a short timeout
    try:
        await page.wait_for_load_state("networkidle", timeout=5000)
    except Exception:
        # If networkidle fails, wait for domcontentloaded or just a short delay
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=3000)
        except Exception:
            # Final fallback: wait for 2 seconds
            await page.wait_for_timeout(2000)
