"""
Unit tests for app/storage_injector.py.
Verifies injection of localStorage, sessionStorage, and cookies into Playwright BrowserContext.
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.storage_injector import inject_storage


@pytest.mark.asyncio
async def test_inject_storage_empty():
    mock_context = AsyncMock()
    await inject_storage(mock_context, {})
    mock_context.add_init_script.assert_not_awaited()
    mock_context.add_cookies.assert_not_awaited()


@pytest.mark.asyncio
async def test_inject_storage_local_and_session_storage():
    mock_context = AsyncMock()
    credentials = {
        "localStorage": {"auth_token": "token123", "theme": "dark"},
        "sessionStorage": {"session_id": "sess-456"},
    }
    await inject_storage(mock_context, credentials)
    mock_context.add_init_script.assert_awaited_once()
    script = mock_context.add_init_script.await_args[0][0]
    assert "auth_token" in script
    assert "token123" in script
    assert "session_id" in script


@pytest.mark.asyncio
async def test_inject_storage_cookies():
    mock_context = AsyncMock()
    credentials = {
        "cookies": [
            {
                "name": "session_cookie",
                "value": "val-abc",
                "domain": "example.com",
                "path": "/",
                "httpOnly": True,
                "secure": True,
            },
            {"invalid_cookie_no_value": "missing name or value"},
            "not-even-a-dict",
        ]
    }
    await inject_storage(mock_context, credentials)
    mock_context.add_cookies.assert_awaited_once()
    cookies = mock_context.add_cookies.await_args[0][0]
    assert len(cookies) == 1
    assert cookies[0]["name"] == "session_cookie"
    assert cookies[0]["value"] == "val-abc"
