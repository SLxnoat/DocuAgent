"""
Integration tests for the full cyclic LangGraph multi-agent pipeline.
Verifies end-to-end execution across Agent 1 -> Agent 2 -> Agent 3 -> Agent 4 -> HITL interrupt.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.langgraph_config import create_docuagent_graph
from app.state import ManualState


@pytest.mark.asyncio
async def test_full_langgraph_pipeline_execution():
    """Verify end-to-end execution of compiled StateGraph with mocked LLMs and browser."""
    initial_state: ManualState = {
        "job_id": "job-integration-graph-001",
        "session_id": "sess-integration-graph-001",
        "target_url": "https://testapp.example.com",
        "raw_input_script": "Open portal. Click login. Enter credentials. View dashboard.",
        "credentials": {"username": "admin", "password": "password123"},
        "structured_steps": [],
        "screenshot_assets": {},
        "markdown_content": "",
        "chat_history": [],
        "execution_logs": [],
        "quality_approved": False,
        "error_states": {},
        "quality_feedback": None,
        "quality_review_attempts": 0,
        "recapture_step_index": None,
    }

    mock_agent1_json = {
        "domain": "Portal",
        "steps": [
            {
                "index": 0,
                "description": "Navigate to login screen",
                "action_type": "navigate",
                "target_selector": "body",
                "input_value": "",
                "selector_hints": ["body"],
            },
            {
                "index": 1,
                "description": "Click Login button",
                "action_type": "click",
                "target_selector": "button#login-btn",
                "input_value": "",
                "selector_hints": [".btn-login"],
            },
        ],
    }

    mock_compiled_md = (
        "# Portal User Guide\n\n"
        "## Prerequisites\n- Modern web browser\n\n"
        "## System Overview\nPortal application overview.\n\n"
        "## Step-by-Step Walkthrough\n"
        "### Step 1: Login\n![Step 0](assets/job-integration-graph-001/step_000.png)\n\n"
        "## Troubleshooting\nContact support if login fails.\n"
    )

    mock_review_feedback = {
        "completeness": {"score": 90, "feedback": "Good"},
        "screenshot_coverage": {"score": 90, "feedback": "Good"},
        "tone_consistency": {"score": 90, "feedback": "Good"},
        "logical_sequencing": {"score": 90, "feedback": "Good"},
        "overall_pass": True,
        "summary": "Document passed quality review.",
    }

    app = create_docuagent_graph()

    # Mock LLM calls, SSRF URL validator, and Playwright browser capture
    # Patch all call sites of validate_target_url to prevent real DNS lookups.
    # Note: playwright_capture_engine uses a local import, so patch source module directly.
    with (
        patch(
            "app.agents.analyzer_agent.ollama_generate_json_with_retry",
            return_value=mock_agent1_json,
        ),
        patch("app.agents.capture_agent.validate_target_url"),
        patch("app.action_dispatcher.validate_target_url"),
        patch("app.utils.url_validator.validate_target_url"),
        patch("app.agents.capture_agent.PlaywrightCaptureEngine") as mock_engine_cls,
        patch("app.technical_writer.ollama_generate_text", return_value=mock_compiled_md),
        patch(
            "app.quality_review.ollama_generate_json_with_retry", return_value=mock_review_feedback
        ),
        patch("app.agents.analyzer_agent.publish_sse_event", new=AsyncMock()),
        patch("app.agents.capture_agent.publish_sse_event", new=AsyncMock()),
        patch("app.technical_writer.publish_sse_event", new=AsyncMock()),
        patch("app.quality_review.publish_sse_event", new=AsyncMock()),
        patch("app.utils.sse_publisher.publish_sse_event", new=AsyncMock()),
    ):
        # Setup mock browser engine context manager
        mock_engine = mock_engine_cls.return_value
        mock_engine.__aenter__ = AsyncMock(return_value=mock_engine)
        mock_engine.__aexit__ = AsyncMock(return_value=None)
        mock_engine.page = AsyncMock()
        mock_engine.context = AsyncMock()

        # Run pipeline
        final_state = await app.ainvoke(
            initial_state,
            config={"configurable": {"thread_id": "test-thread-001"}},
        )

    # Verifications
    # 1. Agent 1 populated structured_steps
    assert len(final_state["structured_steps"]) == 2
    # 2. Agent 2 purged credentials for zero-retention
    assert final_state["credentials"] == {}
    # 3. Agent 3 compiled markdown content
    assert "## Prerequisites" in final_state["markdown_content"]
    assert "## System Overview" in final_state["markdown_content"]
    assert "## Step-by-Step Walkthrough" in final_state["markdown_content"]
    assert "## Troubleshooting" in final_state["markdown_content"]
    # 4. Agent 4 reviewed and approved
    assert final_state["quality_review_attempts"] >= 1
