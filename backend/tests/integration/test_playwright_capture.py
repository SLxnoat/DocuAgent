"""
Integration tests for Playwright browser automation, highlight injection, and screenshot capture.
Verifies real headless browser execution against local mock HTML content.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from app.action_dispatcher import execute_action
from app.dynamic_highlight_injector import (
    cleanup_highlights,
    inject_highlight_effects,
)
from app.playwright_capture_engine import PlaywrightCaptureEngine

MOCK_HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DocuAgent Test Fixture</title>
    <style>
        body { font-family: sans-serif; padding: 40px; background: #f8fafc; }
        .card { background: white; padding: 24px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); width: 400px; }
        .form-group { margin-bottom: 16px; }
        label { display: block; margin-bottom: 6px; font-weight: 600; }
        input { width: 100%; padding: 8px; border: 1px solid #cbd5e1; border-radius: 4px; box-sizing: border-box; }
        button { background: #2563eb; color: white; padding: 10px 16px; border: none; border-radius: 4px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Customer Portal Login</h2>
        <div class="form-group">
            <label for="username">Username</label>
            <input id="username" type="text" placeholder="Enter username" />
        </div>
        <div class="form-group">
            <label for="password">Password</label>
            <input id="password" type="password" placeholder="Enter password" />
        </div>
        <button id="submit-btn" type="button">Sign In</button>
        <p id="status-msg" style="display:none; color: green; margin-top: 12px;">Logged in successfully!</p>
    </div>
    <script>
        document.getElementById('submit-btn').addEventListener('click', () => {
            document.getElementById('status-msg').style.display = 'block';
        });
    </script>
</body>
</html>
"""


@pytest.mark.asyncio
async def test_playwright_highlight_injection_and_cleanup():
    """Verify highlight injection creates overlay in DOM and cleanup removes it."""
    async with PlaywrightCaptureEngine() as engine:
        page = engine.page
        assert page is not None

        # Load mock HTML content
        await page.set_content(MOCK_HTML_PAGE)

        # Inject highlight overlay onto submit button
        await inject_highlight_effects(page, "#submit-btn")

        # Verify overlay element was injected into DOM
        overlay_count = await page.evaluate(
            "() => document.querySelectorAll('.docuagent-highlight-overlay').length"
        )
        assert overlay_count == 1

        backdrop_count = await page.evaluate(
            "() => document.querySelectorAll('.docuagent-backdrop-overlay').length"
        )
        assert backdrop_count == 1

        # Verify cleanup removes overlays completely
        await cleanup_highlights(page)

        overlay_count_after = await page.evaluate(
            "() => document.querySelectorAll('.docuagent-highlight-overlay').length"
        )
        assert overlay_count_after == 0


@pytest.mark.asyncio
async def test_playwright_screenshot_capture_to_disk():
    """Verify screenshot capture writes a valid PNG file to disk."""
    async with PlaywrightCaptureEngine() as engine:
        page = engine.page
        assert page is not None

        await page.set_content(MOCK_HTML_PAGE)
        await inject_highlight_effects(page, "#username")

        with tempfile.TemporaryDirectory() as tmpdir:
            screenshot_path = Path(tmpdir) / "test_step_001.png"

            await page.screenshot(path=str(screenshot_path), full_page=False)

            assert screenshot_path.exists()
            assert screenshot_path.stat().st_size > 0

            # Verify PNG magic bytes
            with screenshot_path.open("rb") as f:
                header = f.read(8)
                assert header == b"\x89PNG\r\n\x1a\n"


@pytest.mark.asyncio
async def test_playwright_action_dispatcher_execution():
    """Verify action dispatcher executes fill and click actions on mock page."""
    async with PlaywrightCaptureEngine() as engine:
        page = engine.page
        assert page is not None

        await page.set_content(MOCK_HTML_PAGE)

        # Type username
        await execute_action(
            page=page,
            action_type="type",
            params={"selector": "#username", "text": "test_operator"},
            context=engine.context,
        )

        input_value = await page.input_value("#username")
        assert input_value == "test_operator"

        # Click submit button
        await execute_action(
            page=page,
            action_type="click",
            params={"selector": "#submit-btn"},
            context=engine.context,
        )

        # Status message should become visible
        is_visible = await page.is_visible("#status-msg")
        assert is_visible is True
