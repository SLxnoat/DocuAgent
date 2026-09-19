"""
Unit tests for Agent 4: Quality & Verification Agent.
Tests evaluation prompt auditing, scoring, rejection loop logic, and conditional edge routing.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest

from app.langgraph_config import route_after_quality_review
from app.quality_review import quality_review_node
from app.state import ManualState


@pytest.fixture
def sample_review_state() -> ManualState:
    return {
        "job_id": "job-review-test-456",
        "session_id": "sess-review-test-456",
        "target_url": "https://portal.example.com",
        "raw_input_script": "Open portal, navigate to settings, update billing email.",
        "credentials": {},
        "structured_steps": [
            {
                "index": 0,
                "description": "Open portal",
                "action_type": "navigate",
                "target_selector": "body",
                "input_value": "",
                "expected_url": "https://portal.example.com",
                "domain_context": "Admin Portal",
                "selector_hints": [],
            }
        ],
        "screenshot_assets": {0: "assets/job-review-test-456/step_000.png"},
        "markdown_content": "# Portal Manual\n## Prerequisites\n## System Overview\n## Step-by-Step Walkthrough\n## Troubleshooting",
        "chat_history": [],
        "execution_logs": [],
        "quality_approved": False,
        "error_states": {},
        "quality_feedback": None,
        "quality_review_attempts": 0,
        "recapture_step_index": None,
    }


@pytest.mark.asyncio
async def test_quality_review_approval(sample_review_state):
    """Test approval when all criteria score >= 80."""
    mock_feedback = {
        "completeness": {"score": 90, "feedback": "All sections well documented."},
        "screenshot_coverage": {"score": 95, "feedback": "Screenshots cover all steps."},
        "tone_consistency": {"score": 88, "feedback": "Tone is professional."},
        "logical_sequencing": {"score": 92, "feedback": "Flow is logical."},
        "overall_pass": True,
        "summary": "Document meets all release standards.",
    }

    with (
        patch("app.quality_review.ollama_generate_json_with_retry", return_value=mock_feedback),
        patch("app.quality_review.publish_sse_event", new=AsyncMock()),
    ):
        result = await quality_review_node(sample_review_state)

    assert result["quality_review_attempts"] == 1
    feedback = json.loads(result["quality_feedback"])
    assert feedback["overall_pass"] is True

    # Check routing edge
    next_node = route_after_quality_review(result)
    assert next_node == "chat_refiner_node"


@pytest.mark.asyncio
async def test_quality_review_rejection_loops_back(sample_review_state):
    """Test rejection when criteria < 80 routes back to compile_markdown_node."""
    mock_feedback = {
        "completeness": {"score": 60, "feedback": "Troubleshooting section is too sparse."},
        "screenshot_coverage": {"score": 85, "feedback": "Screenshots present."},
        "tone_consistency": {"score": 80, "feedback": "Tone acceptable."},
        "logical_sequencing": {"score": 85, "feedback": "Sequence is fine."},
        "overall_pass": False,
        "summary": "Needs expansion on troubleshooting steps.",
    }

    with (
        patch("app.quality_review.ollama_generate_json_with_retry", return_value=mock_feedback),
        patch("app.quality_review.publish_sse_event", new=AsyncMock()),
    ):
        result = await quality_review_node(sample_review_state)

    assert result["quality_review_attempts"] == 1
    feedback = json.loads(result["quality_feedback"])
    assert feedback["overall_pass"] is False

    # Attempt 1 failed -> should loop back to compiler
    next_node = route_after_quality_review(result)
    assert next_node == "compile_markdown_node"


@pytest.mark.asyncio
async def test_quality_review_max_retries_forced_approval(sample_review_state):
    """Test that after 3 failed attempts, loop guard forces approval to chat_refiner_node."""
    sample_review_state["quality_review_attempts"] = 2  # This call will become attempt 3

    mock_feedback = {
        "completeness": {"score": 65, "feedback": "Still slightly incomplete."},
        "screenshot_coverage": {"score": 70, "feedback": "Missing one image."},
        "tone_consistency": {"score": 70, "feedback": "Minor tone issues."},
        "logical_sequencing": {"score": 70, "feedback": "Minor flow issues."},
        "overall_pass": False,
        "summary": "Third attempt failed.",
    }

    with (
        patch("app.quality_review.ollama_generate_json_with_retry", return_value=mock_feedback),
        patch("app.quality_review.publish_sse_event", new=AsyncMock()),
    ):
        result = await quality_review_node(sample_review_state)

    assert result["quality_review_attempts"] == 3

    # On attempt 3, loop guard halts re-generation and routes to chat_refiner_node
    next_node = route_after_quality_review(result)
    assert next_node == "chat_refiner_node"
