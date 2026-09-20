"""
Unit tests for action_dispatcher._type() — DEFECT-006 regression tests.
Verifies that:
- _type uses locator.fill() instead of deprecated page.type()
- _type falls back to triple_click + press_sequentially for contenteditable inputs
- element.clear() (Selenium API) is never called
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.action_dispatcher import execute_action


def _make_page(locator=None):
    """Build a MagicMock page where async methods are AsyncMocks."""
    mock_page = MagicMock()
    mock_page.evaluate = AsyncMock()
    mock_page.wait_for_selector = AsyncMock()
    mock_page.type = AsyncMock()  # deprecated — should NOT be called
    if locator is not None:
        mock_page.locator.return_value.first = locator
    return mock_page


@pytest.mark.asyncio
async def test_type_uses_locator_fill_not_page_type():
    """Verify that the type action calls locator.fill() instead of deprecated page.type()."""
    mock_locator = AsyncMock()
    mock_page = _make_page(locator=mock_locator)

    await execute_action(
        page=mock_page,
        action_type="type",
        params={"selector": "input#username", "text": "admin"},
    )

    # Must use locator.fill — never page.type
    mock_locator.fill.assert_awaited_once_with("admin")
    mock_page.type.assert_not_called()

    # element.clear() must not be called — it doesn't exist in Playwright
    mock_locator.clear.assert_not_called()


@pytest.mark.asyncio
async def test_type_fallback_to_press_sequentially_when_fill_fails():
    """Verify fallback to triple_click + press_sequentially when fill() raises."""
    mock_locator = AsyncMock()
    mock_locator.fill.side_effect = Exception("element is not an <input>")
    mock_page = _make_page(locator=mock_locator)

    await execute_action(
        page=mock_page,
        action_type="type",
        params={"selector": "[contenteditable]", "text": "Hello World"},
    )

    mock_locator.triple_click.assert_awaited_once()
    mock_locator.press_sequentially.assert_awaited_once()
    call_args = mock_locator.press_sequentially.await_args
    assert call_args[0][0] == "Hello World"
    assert "delay" in call_args[1]


@pytest.mark.asyncio
async def test_type_requires_selector():
    """Verify ValueError is raised if selector is missing."""
    mock_page = _make_page()
    with pytest.raises(ValueError, match="selector"):
        await execute_action(
            page=mock_page,
            action_type="type",
            params={"text": "hello"},
        )


@pytest.mark.asyncio
async def test_type_requires_text():
    """Verify ValueError is raised if text is None (empty string is allowed)."""
    mock_locator = AsyncMock()
    mock_page = _make_page(locator=mock_locator)

    with pytest.raises(ValueError, match="text"):
        await execute_action(
            page=mock_page,
            action_type="type",
            params={"selector": "input", "text": None},
        )
