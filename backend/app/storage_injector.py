"""
Storage injection utilities for DocuAgent AI.
Provides functions to inject pre-authenticated data into browser storage (localStorage, sessionStorage, cookies).
"""

from typing import Any

from playwright.async_api import BrowserContext


async def inject_storage(
    context: BrowserContext,
    credentials: dict[str, Any],
) -> None:
    """
    Inject pre-authenticated data into browser storage (localStorage, sessionStorage, cookies).
    This function is intended to be used before navigation to set up an authenticated session
    without going through the login form.

    Args:
        context: Playwright BrowserContext object
        credentials: Dictionary containing storage data to inject. Expected structure:
            {
                "localStorage": {"key": "value", ...},
                "sessionStorage": {"key": "value", ...},
                "cookies": [
                    {"name": "cookie_name", "value": "cookie_value", "domain": ".example.com", "path": "/", ...},
                    ...
                ]
            }
            Note: Only the keys that are present will be processed.

    Returns:
        None
    """
    # Prepare the init script for localStorage and sessionStorage
    init_script = ""
    local_storage_data = credentials.get("localStorage")
    if local_storage_data and isinstance(local_storage_data, dict):
        # Escape quotes and newlines for JavaScript string
        import json

        local_storage_json = json.dumps(local_storage_data)
        init_script += f"""
        // Inject localStorage
        const localStorageData = {local_storage_json};
        for (const [key, value] of Object.entries(localStorageData)) {{
            localStorage.setItem(key, value);
        }}
        """

    session_storage_data = credentials.get("sessionStorage")
    if session_storage_data and isinstance(session_storage_data, dict):
        import json

        session_storage_json = json.dumps(session_storage_data)
        init_script += f"""
        // Inject sessionStorage
        const sessionStorageData = {session_storage_json};
        for (const [key, value] of Object.entries(sessionStorageData)) {{
            sessionStorage.setItem(key, value);
        }}
        """

    # If we have any init script, add it to the context
    if init_script:
        await context.add_init_script(init_script)

    # Inject cookies
    cookies_data = credentials.get("cookies")
    if cookies_data and isinstance(cookies_data, list):
        # Prepare cookies for Playwright's add_cookies method
        formatted_cookies = []
        for cookie in cookies_data:
            if not isinstance(cookie, dict):
                continue
            # Required fields: name, value
            name = cookie.get("name")
            value = cookie.get("value")
            if name is None or value is None:
                continue
            formatted_cookie = {
                "name": name,
                "value": value,
                "domain": cookie.get("domain"),
                "path": cookie.get("path", "/"),
                "expires": cookie.get("expires"),  # UNIX timestamp, optional
                "httpOnly": cookie.get("httpOnly", False),
                "secure": cookie.get("secure", False),
                "sameSite": cookie.get("sameSite"),  # Can be "Strict", "Lax", "None"
            }
            # Remove None values to avoid passing them as undefined
            formatted_cookie = {k: v for k, v in formatted_cookie.items() if v is not None}
            formatted_cookies.append(formatted_cookie)

        if formatted_cookies:
            await context.add_cookies(formatted_cookies)
