"""
Unit tests for app/capture_engine.py.
Verifies element screenshot capture, viewport fallback, and error placeholder generation.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.capture_engine import (
    capture_screenshot_with_fallback,
    capture_viewport_screenshot,
)


@pytest.mark.asyncio
async def test_capture_viewport_screenshot_success(tmp_path):
    mock_page = AsyncMock()
    with patch("app.capture_engine.settings.assets_dir", str(tmp_path)):
        path = await capture_viewport_screenshot(
            page=mock_page,
            job_id="job-111",
            step_index=0,
        )
        assert "step_000.png" in path
        mock_page.screenshot.assert_awaited_once()


@pytest.mark.asyncio
async def test_capture_viewport_screenshot_error(tmp_path):
    mock_page = AsyncMock()
    mock_page.screenshot.side_effect = RuntimeError("Browser crashed")
    state = {"error_states": {}}

    with patch("app.capture_engine.settings.assets_dir", str(tmp_path)):
        with pytest.raises(RuntimeError):
            await capture_viewport_screenshot(
                page=mock_page,
                job_id="job-111",
                step_index=1,
                state=state,
            )
        assert "1" in state["error_states"]


@pytest.mark.asyncio
async def test_capture_screenshot_with_fallback_primary_success(tmp_path):
    mock_page = AsyncMock()
    mock_element = AsyncMock()
    mock_page.query_selector.return_value = mock_element

    with patch("app.capture_engine.settings.assets_dir", str(tmp_path)):
        path = await capture_screenshot_with_fallback(
            page=mock_page,
            job_id="job-222",
            step_index=2,
            primary_selector="#main-btn",
            selector_hints=[".btn-alt"],
        )
        assert "step_002.png" in path
        mock_element.screenshot.assert_awaited_once()


@pytest.mark.asyncio
async def test_capture_screenshot_with_fallback_falls_to_viewport(tmp_path):
    mock_page = AsyncMock()
    # Selector fails
    mock_page.wait_for_selector.side_effect = Exception("Selector not found")

    with patch("app.capture_engine.settings.assets_dir", str(tmp_path)):
        path = await capture_screenshot_with_fallback(
            page=mock_page,
            job_id="job-333",
            step_index=3,
            primary_selector="#missing",
            selector_hints=[],
        )
        assert "step_003.png" in path
        mock_page.screenshot.assert_awaited_once()


@pytest.mark.asyncio
async def test_capture_screenshot_with_fallback_all_fail_returns_placeholder(tmp_path):
    mock_page = AsyncMock()
    mock_page.wait_for_selector.side_effect = Exception("Selector not found")
    mock_page.screenshot.side_effect = Exception("Viewport capture failed")
    state = {"error_states": {}}

    with patch("app.capture_engine.settings.assets_dir", str(tmp_path)):
        result = await capture_screenshot_with_fallback(
            page=mock_page,
            job_id="job-444",
            step_index=4,
            primary_selector="#missing",
            selector_hints=[],
            state=state,
            step_description="Submit purchase order",
        )
        assert result == "PLACEHOLDER:Submit purchase order"
        assert "4" in state["error_states"]
