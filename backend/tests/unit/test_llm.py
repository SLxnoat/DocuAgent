"""
Unit tests for app/llm.py — Sprint 2 verification.
Tests both asynchronous (httpx.AsyncClient) and synchronous (httpx.Client) LLM functions,
domain classification, and selector fallbacks.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.llm import (
    ADMIN_PORTAL_DOMAIN,
    CRM_DOMAIN,
    ECOMMERCE_DOMAIN,
    FINANCE_DOMAIN,
    SAAS_DOMAIN,
    async_ollama_generate_json,
    async_ollama_generate_json_with_retry,
    async_ollama_generate_text,
    classify_domain,
    generate_selector_fallbacks,
    get_ollama_analyzer_url,
    get_ollama_primary_url,
    ollama_generate_json,
    ollama_generate_json_with_retry,
    ollama_generate_text,
)


def test_urls():
    assert "/api/generate" in get_ollama_analyzer_url()
    assert "/api/generate" in get_ollama_primary_url()


# ------------------------------------------------------------------------------
# Async LLM tests
# ------------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_async_ollama_generate_json_success():
    expected = {"steps": [{"index": 1, "description": "click button"}]}
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": json.dumps(expected)}
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response

    result = await async_ollama_generate_json(
        prompt="Analyze this script",
        model="qwen2.5:72b",
        temperature=0.1,
        max_tokens=1000,
        client=mock_client,
    )
    assert result == expected
    mock_client.post.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_ollama_generate_json_decode_error():
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "Invalid json string {"}
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response

    with pytest.raises(ValueError, match="Failed to parse JSON"):
        await async_ollama_generate_json(prompt="Test", client=mock_client)


@pytest.mark.asyncio
async def test_async_ollama_generate_json_with_retry_succeeds_second_try():
    bad_response = MagicMock()
    bad_response.json.return_value = {"response": "bad json"}
    bad_response.raise_for_status = MagicMock()

    good_response = MagicMock()
    good_response.json.return_value = {"response": json.dumps({"status": "ok"})}
    good_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post.side_effect = [bad_response, good_response]

    result = await async_ollama_generate_json_with_retry(
        prompt="Test retry",
        max_retries=2,
        client=mock_client,
    )
    assert result == {"status": "ok"}
    assert mock_client.post.await_count == 2


@pytest.mark.asyncio
async def test_async_ollama_generate_json_with_retry_raises_network_error():
    mock_client = AsyncMock()
    mock_client.post.side_effect = httpx.ConnectError("Connection refused")

    with pytest.raises(httpx.ConnectError):
        await async_ollama_generate_json_with_retry(
            prompt="Test network failure",
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_async_ollama_generate_text_success():
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "# Generated Manual"}
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response

    result = await async_ollama_generate_text(
        prompt="Write markdown",
        model="llama3.3:70b",
        temperature=0.2,
        client=mock_client,
    )
    assert result == "# Generated Manual"


# ------------------------------------------------------------------------------
# Sync LLM tests
# ------------------------------------------------------------------------------


def test_sync_ollama_generate_json_success():
    expected = {"key": "value"}
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": json.dumps(expected)}
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.Client") as mock_client_cls:
        mock_instance = MagicMock()
        mock_instance.post.return_value = mock_response
        mock_client_cls.return_value.__enter__.return_value = mock_instance

        res = ollama_generate_json("prompt", max_tokens=500)
        assert res == expected


def test_sync_ollama_generate_json_with_retry():
    bad_resp = MagicMock()
    bad_resp.json.return_value = {"response": "bad"}
    bad_resp.raise_for_status = MagicMock()

    good_resp = MagicMock()
    good_resp.json.return_value = {"response": '{"data": 123}'}
    good_resp.raise_for_status = MagicMock()

    with patch("httpx.Client") as mock_client_cls:
        mock_instance = MagicMock()
        mock_instance.post.side_effect = [bad_resp, good_resp]
        mock_client_cls.return_value.__enter__.return_value = mock_instance

        res = ollama_generate_json_with_retry("prompt", max_retries=1)
        assert res == {"data": 123}


def test_sync_ollama_generate_text():
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "Hello LLM"}
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.Client") as mock_client_cls:
        mock_instance = MagicMock()
        mock_instance.post.return_value = mock_response
        mock_client_cls.return_value.__enter__.return_value = mock_instance

        text = ollama_generate_text("prompt")
        assert text == "Hello LLM"


# ------------------------------------------------------------------------------
# Domain Classification Tests
# ------------------------------------------------------------------------------


def test_classify_domain_ecommerce():
    domain = classify_domain("https://shop.example.com", "Add product to cart and checkout")
    assert domain == ECOMMERCE_DOMAIN


def test_classify_domain_crm():
    domain = classify_domain(
        "https://hubspot.com", "Add new customer contact to the sales pipeline"
    )
    assert domain == CRM_DOMAIN


def test_classify_domain_finance():
    domain = classify_domain("https://bank.example.com", "Transfer funds and pay invoice")
    assert domain == FINANCE_DOMAIN


def test_classify_domain_admin_portal():
    domain = classify_domain("https://portal.example.com", "Go to admin control panel settings")
    assert domain == ADMIN_PORTAL_DOMAIN


def test_classify_domain_default():
    domain = classify_domain("https://xyz.io", "Random text without keywords")
    assert domain == SAAS_DOMAIN


# ------------------------------------------------------------------------------
# Selector Fallbacks Tests
# ------------------------------------------------------------------------------


def test_generate_selector_fallbacks_id():
    fallbacks = generate_selector_fallbacks("#submit-btn")
    assert any('[id="submit-btn"]' in fb for fb in fallbacks)


def test_generate_selector_fallbacks_class():
    fallbacks = generate_selector_fallbacks(".btn-primary")
    assert any("btn-primary" in fb for fb in fallbacks)


def test_generate_selector_fallbacks_attr():
    fallbacks = generate_selector_fallbacks("[data-testid='login']")
    assert len(fallbacks) >= 2


def test_generate_selector_fallbacks_tag():
    fallbacks = generate_selector_fallbacks("button")
    assert len(fallbacks) >= 2
    assert len(fallbacks) <= 3
