"""
Global pytest configuration and fixtures for DocuAgent AI.
"""

from __future__ import annotations

import os
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

# Ensure dev test environment settings
os.environ["APP_ENV"] = "testing"
os.environ["SECRET_KEY"] = "test-secret-key-for-unit-testing-only-12345"
os.environ["API_TOKEN"] = "test-api-token-value"
os.environ["ASSETS_DIR"] = "/tmp/docuagent_test_assets"
os.environ["EXPORTS_DIR"] = "/tmp/docuagent_test_exports"


@pytest.fixture
def sample_script() -> str:
    """Return a standard test workflow script."""
    return (
        "Log in to the dashboard with admin credentials. "
        "Navigate to the Users management section. "
        "Click on Add New User button and fill in username and email. "
        "Save the new user and verify that the user appears in the user list."
    )


@pytest.fixture
def sample_structured_steps() -> list[dict[str, Any]]:
    """Return sample structured steps for technical writer and reviewer tests."""
    return [
        {
            "index": 0,
            "description": "Navigate to the login page and authenticate with username and password.",
            "action_type": "authenticate",
            "target_selector": "input#username",
            "input_value": "admin",
            "expected_url": "https://example.com/login",
            "domain_context": "Admin Portal",
            "selector_hints": ["#login-form", "button[type='submit']"],
        },
        {
            "index": 1,
            "description": "Click on the Users navigation item in the sidebar.",
            "action_type": "click",
            "target_selector": "nav a[href='/users']",
            "input_value": "",
            "expected_url": "https://example.com/users",
            "domain_context": "Admin Portal",
            "selector_hints": [".sidebar-nav-users", "text='Users'"],
        },
        {
            "index": 2,
            "description": "Click the Add User button to open the creation dialog.",
            "action_type": "click",
            "target_selector": "button#add-user-btn",
            "input_value": "",
            "expected_url": "https://example.com/users",
            "domain_context": "Admin Portal",
            "selector_hints": [".btn-create-user", "text='Add User'"],
        },
    ]


@pytest.fixture
def mock_llm_response():
    """Helper to mock Ollama / LangChain invoke responses."""

    def _create_mock(content: str):
        mock = MagicMock()
        mock.content = content
        mock.ainvoke = AsyncMock(return_value=mock)
        mock.invoke = MagicMock(return_value=mock)
        return mock

    return _create_mock


TEST_API_TOKEN = "test-api-token-value"
AUTH_HEADERS = {"Authorization": f"Bearer {TEST_API_TOKEN}"}


@pytest.fixture
def authed_client():
    """
    Return a FastAPI TestClient pre-configured with the test Bearer token header.
    Use this fixture in tests that hit authenticated API routes.
    """
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, headers=AUTH_HEADERS)
