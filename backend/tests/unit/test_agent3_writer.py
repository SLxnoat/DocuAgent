"""
Unit tests for Agent 3: Technical Writer & Layout Agent.
Verifies Markdown document structure, screenshot mapping, callouts, and quality loop handling.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.state import ManualState
from app.technical_writer import compile_markdown_node


@pytest.fixture
def sample_writer_state() -> ManualState:
    return {
        "job_id": "job-test-writer-123",
        "session_id": "sess-test-writer-123",
        "target_url": "https://dashboard.example.com",
        "raw_input_script": "Login to dashboard, go to user profile, update display name.",
        "credentials": {},
        "structured_steps": [
            {
                "index": 0,
                "description": "Navigate to login screen and authenticate",
                "action_type": "authenticate",
                "target_selector": "#login-form",
                "input_value": "",
                "expected_url": "https://dashboard.example.com/login",
                "domain_context": "SaaS Platform",
                "selector_hints": ["#login", "form.auth"],
            },
            {
                "index": 1,
                "description": "Click on Profile in the navigation dropdown",
                "action_type": "click",
                "target_selector": "button#profile-dropdown",
                "input_value": "",
                "expected_url": "https://dashboard.example.com/profile",
                "domain_context": "SaaS Platform",
                "selector_hints": [".user-avatar", "a[href='/profile']"],
            },
        ],
        "screenshot_assets": {
            0: "assets/job-test-writer-123/step_000.png",
            1: "assets/job-test-writer-123/step_001.png",
        },
        "markdown_content": "",
        "chat_history": [],
        "execution_logs": [],
        "quality_approved": False,
        "error_states": {},
        "quality_feedback": None,
        "quality_review_attempts": 0,
        "recapture_step_index": None,
    }


@pytest.mark.asyncio
async def test_compile_markdown_generates_standard_sections(sample_writer_state):
    """Verify generated document contains Prerequisites, System Overview, Walkthrough, and Troubleshooting."""
    mock_md = """# User Profile Update Manual

## Prerequisites
- Modern web browser (Chrome 110+, Firefox 110+)
- Valid SaaS account credentials

## System Overview
The SaaS Platform dashboard allows users to manage their profiles and permissions.

## Step-by-Step Walkthrough

### Step 1: Login to Dashboard
Navigate to the login screen and enter credentials.
![Step 0](assets/job-test-writer-123/step_000.png)

> 💡 Tip: Keep your login session secure by logging out on shared devices.

### Step 2: Access User Profile
Click on the Profile dropdown in the top navigation bar.
![Step 1](assets/job-test-writer-123/step_001.png)

## Troubleshooting
If the dropdown menu fails to open, refresh the page and verify browser JavaScript is enabled.
"""

    with (
        patch("app.technical_writer.ollama_generate_text", return_value=mock_md),
        patch("app.technical_writer.publish_sse_event", new=AsyncMock()),
    ):
        result = await compile_markdown_node(sample_writer_state)

    md = result["markdown_content"]
    assert "## Prerequisites" in md
    assert "## System Overview" in md
    assert "## Step-by-Step Walkthrough" in md
    assert "## Troubleshooting" in md
    assert "assets/job-test-writer-123/step_000.png" in md
    assert "assets/job-test-writer-123/step_001.png" in md


@pytest.mark.asyncio
async def test_compile_markdown_incorporates_quality_feedback(sample_writer_state):
    """Verify that quality_feedback from Agent 4 rejection is passed to writer prompt."""
    sample_writer_state["quality_feedback"] = "Missing troubleshooting steps for network timeouts."
    sample_writer_state["quality_review_attempts"] = 1

    captured_prompt = None

    def mock_generate(prompt, **kwargs):
        nonlocal captured_prompt
        captured_prompt = prompt
        return "# Revised Manual\n## Prerequisites\n## System Overview\n## Step-by-Step Walkthrough\n## Troubleshooting"

    with (
        patch("app.technical_writer.ollama_generate_text", side_effect=mock_generate),
        patch("app.technical_writer.publish_sse_event", new=AsyncMock()),
    ):
        result = await compile_markdown_node(sample_writer_state)

    assert "Missing troubleshooting steps for network timeouts." in captured_prompt
    assert result["markdown_content"].startswith("# Revised Manual")


@pytest.mark.asyncio
async def test_compile_markdown_error_fallback(sample_writer_state):
    """Verify that LLM failure produces structured fallback markdown without crashing."""
    with (
        patch(
            "app.technical_writer.ollama_generate_text",
            side_effect=RuntimeError("Ollama inference timeout"),
        ),
        patch("app.technical_writer.publish_sse_event", new=AsyncMock()),
    ):
        result = await compile_markdown_node(sample_writer_state)

    md = result["markdown_content"]
    assert "# Technical Documentation" in md
    assert "## Prerequisites" in md
    assert "## Troubleshooting" in md
    assert "LLM error" in md
