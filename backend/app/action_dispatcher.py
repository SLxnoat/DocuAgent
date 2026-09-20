"""
Action Execution Dispatcher for DocuAgent AI.
Provides a centralized dispatcher for executing various Playwright actions.
"""

import random
from typing import Any

from playwright.async_api import BrowserContext, Page

from app.auth_handler import handle_login
from app.storage_injector import inject_storage
from app.utils.url_validator import validate_target_url


async def execute_action(
    page: Page,
    action_type: str,
    params: dict[str, Any] | None = None,
    context: BrowserContext | None = None,
) -> None:
    """
    Execute a specified action on the Playwright page.

    Args:
        page: Playwright Page object to perform the action on
        action_type: Type of action to execute. Supported actions:
            - "navigate": Navigate to a URL (requires 'url' in params)
            - "click": Click an element (requires 'selector' in params)
            - "type": Type text into an element (requires 'selector' and 'text' in params)
            - "scroll": Scroll the page (optional 'x' and 'y' in params, defaults to 0,0)
            - "wait": Wait for a condition (requires 'timeout' in ms, 'selector' to wait for visibility, or 'state' for load state)
            - "authenticate": Perform authentication (requires 'username' and 'password' in params)
        params: Dictionary of parameters for the action (varies by action type)
                For wait action: can include 'timeout' (ms), 'selector' (to wait for visibility), or 'state' ('networkidle' or 'domcontentloaded')
        context: Optional BrowserContext for actions that need it (like authenticate with storage injection)

    Raises:
        ValueError: If an unsupported action_type is provided or required parameters are missing
        Exception: Any exception from the underlying Playwright operations
    """
    if params is None:
        params = {}

    if action_type == "navigate":
        await _navigate(page, params)
    elif action_type == "click":
        await _click(page, params)
    elif action_type == "type":
        await _type(page, params)
    elif action_type == "scroll":
        await _scroll(page, params)
    elif action_type == "wait":
        await _wait(page, params)
    elif action_type == "authenticate":
        await _authenticate(page, params, context)
    else:
        raise ValueError(f"Unsupported action type: {action_type}")


async def _navigate(page: Page, params: dict[str, Any]) -> None:
    """
    Navigate to a URL with intelligent wait states.

    Args:
        page: Playwright Page object
        params: Must contain 'url' key
    """
    url = params.get("url")
    if not url:
        raise ValueError("Navigate action requires 'url' parameter")

    # Validate URL for SSRF protection
    validate_target_url(url)

    # Navigate to the URL with intelligent wait states
    # Try networkidle first, fall back to domcontentloaded
    try:
        await page.goto(url)
        await page.wait_for_load_state("networkidle", timeout=10000)
    except Exception:
        # Fallback to domcontentloaded if networkidle fails or times out
        await page.wait_for_load_state("domcontentloaded", timeout=10000)


async def _click(page: Page, params: dict[str, Any]) -> None:
    """
    Click an element with automatic scroll-into-view.

    Args:
        page: Playwright Page object
        params: Must contain 'selector' key
    """
    selector = params.get("selector")
    if not selector:
        raise ValueError("Click action requires 'selector' parameter")

    # Scroll the element into view, then wait for it to be attached and visible, then click
    await page.evaluate(
        f"document.querySelector('{selector}')?.scrollIntoView({{behavior: 'smooth', block: 'center', inline: 'nearest'}});"
    )
    await page.wait_for_selector(selector, state="visible", timeout=5000)
    await page.click(selector)


async def _type(page: Page, params: dict[str, Any]) -> None:
    """
    Type text into an element using the modern Playwright Locator API.

    Per DOC-005 Section 5, the ``type`` action uses:
    - ``locator.fill()`` to atomically clear existing content and set the new value
      (works for most standard HTML inputs and textareas).
    - ``locator.press_sequentially()`` as a fallback for inputs that react to
      individual keystrokes (e.g. autocomplete, masked inputs), simulating
      human-like typing at a configurable delay.

    ``page.type()`` (Playwright Page-level API) is **deprecated** in Playwright
    ≥1.38 and ``element.clear()`` does not exist in the Playwright Python SDK
    (it is a Selenium-only API). This implementation replaces both.

    Args:
        page: Playwright Page object
        params: Must contain 'selector' and 'text' keys
    """
    selector = params.get("selector")
    text = params.get("text")
    if not selector:
        raise ValueError("Type action requires 'selector' parameter")
    if text is None:  # Allow empty string but not None
        raise ValueError("Type action requires 'text' parameter")

    # Scroll the element into view before interacting
    await page.evaluate(
        f"document.querySelector('{selector}')?.scrollIntoView({{behavior: 'smooth', block: 'center', inline: 'nearest'}});"
    )
    await page.wait_for_selector(selector, state="visible", timeout=5000)

    locator = page.locator(selector).first

    # Use fill() to atomically clear the existing value and set the new one.
    # This is the recommended Playwright approach and works for the vast majority
    # of standard <input> and <textarea> elements.
    try:
        await locator.fill(text)
    except Exception:
        # Fallback: for inputs that do not support fill() (e.g. contenteditable,
        # custom components), use triple-click to select all and then type
        # character-by-character with a human-like delay.
        delay_ms = random.uniform(30, 50)
        await locator.triple_click()
        await locator.press_sequentially(text, delay=delay_ms)


async def _scroll(page: Page, params: dict[str, Any]) -> None:
    """
    Scroll the page.

    Args:
        page: Playwright Page object
        params: Optional 'x' and 'y' keys for scroll position (defaults to 0,0)
    """
    x = params.get("x", 0)
    y = params.get("y", 0)
    await page.evaluate(f"window.scrollTo({x}, {y})")


async def _wait(page: Page, params: dict[str, Any]) -> None:
    """
    Wait for a condition with intelligent wait states.

    Args:
        page: Playwright Page object
        params: Dictionary that can contain:
            - 'timeout': Wait for specified timeout in ms
            - 'selector': Wait for selector to be visible
            - 'state': Wait for load state ('networkidle' or 'domcontentloaded')
                       If 'networkidle' fails, falls back to 'domcontentloaded'
    """
    timeout = params.get("timeout")
    selector = params.get("selector")
    state = params.get("state")

    if state is not None:
        # Wait for load state with fallback
        try:
            if state == "networkidle":
                await page.wait_for_load_state("networkidle", timeout=10000)
            elif state == "domcontentloaded":
                await page.wait_for_load_state("domcontentloaded", timeout=10000)
            else:
                # Default to networkidle with fallback for unknown states
                try:
                    await page.wait_for_load_state("networkidle", timeout=10000)
                except Exception:
                    await page.wait_for_load_state("domcontentloaded", timeout=10000)
        except Exception:
            # If networkidle fails, fall back to domcontentloaded
            await page.wait_for_load_state("domcontentloaded", timeout=10000)
    elif timeout is not None:
        # Wait for specified timeout
        await page.wait_for_timeout(timeout)
    elif selector is not None:
        # Wait for selector to be visible
        await page.wait_for_selector(selector, state="visible", timeout=5000)
    else:
        raise ValueError("Wait action requires either 'timeout', 'selector', or 'state' parameter")


async def _authenticate(page: Page, params: dict[str, Any], context: BrowserContext | None) -> None:
    """
    Perform authentication using username and password.

    Args:
        page: Playwright Page object
        params: Must contain 'username' and 'password' keys
        context: Optional BrowserContext for storage injection after login
    """
    username = params.get("username")
    password = params.get("password")
    if not username or not password:
        raise ValueError("Authenticate action requires 'username' and 'password' parameters")

    # Perform login using the auth handler
    await handle_login(page, username, password)

    # If context is provided and we have storage credentials, inject them
    # Note: In a full implementation, we would get credentials from the state
    # For now, we'll just note that storage injection would happen here
    # The actual storage data would need to be passed in params or retrieved from state
    storage_data = params.get("storage")
    if context and storage_data:
        await inject_storage(context, storage_data)
