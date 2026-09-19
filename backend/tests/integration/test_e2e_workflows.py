"""
End-to-End functional integration tests covering:
- Complete user flow (generate -> editor -> export)
- Chat refinement flow
- Screenshot re-capture flow
- Fault tolerance against invalid CSS selectors
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from app.chat_refiner import chat_refiner_node
from app.langgraph_config import create_docuagent_graph
from app.services.export_service import export_document
from app.state import ManualState


@pytest.fixture
def mock_pipeline_data():
    mock_agent1_json = {
        "domain": "Settings App",
        "steps": [
            {
                "index": 0,
                "description": "Navigate to settings",
                "action_type": "navigate",
                "target_selector": "body",
                "input_value": "",
                "selector_hints": ["body"],
            },
            {
                "index": 1,
                "description": "Click dark mode toggle",
                "action_type": "click",
                "target_selector": "button#theme-toggle",
                "input_value": "",
                "selector_hints": [".toggle"],
            },
        ],
    }

    mock_compiled_md = (
        "# Settings App Manual\n\n"
        "## Prerequisites\n- Active account\n\n"
        "## System Overview\nSettings portal guide.\n\n"
        "## Step-by-Step Walkthrough\n"
        "### Step 1: Open Settings\n\n"
        "### Step 2: Toggle Theme\n\n"
        "## Troubleshooting\nRefresh if toggle fails.\n"
    )

    mock_review_pass = {
        "completeness": {"score": 95, "feedback": "Excellent"},
        "screenshot_coverage": {"score": 95, "feedback": "Good"},
        "tone_consistency": {"score": 90, "feedback": "Consistent"},
        "logical_sequencing": {"score": 95, "feedback": "Logical"},
        "overall_pass": True,
        "summary": "Document passed review.",
    }

    return mock_agent1_json, mock_compiled_md, mock_review_pass


@pytest.mark.asyncio
async def test_e2e_complete_generation_and_export_flow(mock_pipeline_data, monkeypatch):
    """E2E Test: Submit script -> generate document -> export to PDF."""
    mock_agent1, mock_compiled_md, mock_review = mock_pipeline_data
    job_id = "e2e-job-001"

    with tempfile.TemporaryDirectory() as tmpdir:
        assets_dir = Path(tmpdir) / "assets"
        exports_dir = Path(tmpdir) / "exports"
        assets_dir.mkdir()
        exports_dir.mkdir()

        import app.config as cfg

        monkeypatch.setattr(cfg.settings, "assets_dir", str(assets_dir))
        monkeypatch.setattr(cfg.settings, "exports_dir", str(exports_dir))

        state: ManualState = {
            "job_id": job_id,
            "session_id": "e2e-sess-001",
            "target_url": "https://portal.example.com",
            "raw_input_script": "Go to settings and toggle dark mode.",
            "credentials": {"username": "admin", "password": "secret"},
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

        app = create_docuagent_graph()

        with (
            patch(
                "app.agents.analyzer_agent.ollama_generate_json_with_retry",
                return_value=mock_agent1,
            ),
            patch("app.agents.capture_agent.validate_target_url"),
            patch("app.action_dispatcher.validate_target_url"),
            patch("app.utils.url_validator.validate_target_url"),
            patch("app.agents.capture_agent.PlaywrightCaptureEngine") as mock_engine_cls,
            patch("app.technical_writer.ollama_generate_text", return_value=mock_compiled_md),
            patch("app.quality_review.ollama_generate_json_with_retry", return_value=mock_review),
            patch("app.agents.analyzer_agent.publish_sse_event", new=AsyncMock()),
            patch("app.agents.capture_agent.publish_sse_event", new=AsyncMock()),
            patch("app.technical_writer.publish_sse_event", new=AsyncMock()),
            patch("app.quality_review.publish_sse_event", new=AsyncMock()),
        ):
            mock_engine = mock_engine_cls.return_value
            mock_engine.__aenter__ = AsyncMock(return_value=mock_engine)
            mock_engine.__aexit__ = AsyncMock(return_value=None)
            mock_engine.page = AsyncMock()
            mock_engine.context = AsyncMock()

            # Execute pipeline
            final_state = await app.ainvoke(
                state,
                config={"configurable": {"thread_id": "e2e-thread-001"}},
            )

        assert final_state["quality_approved"] is True
        assert len(final_state["markdown_content"]) > 0

        # Now export the generated markdown to PDF
        pdf_path = export_document(
            job_id=job_id,
            markdown_content=final_state["markdown_content"],
            fmt="pdf",
        )
        assert Path(pdf_path).exists()
        assert Path(pdf_path).stat().st_size > 0


@pytest.mark.asyncio
async def test_e2e_refinement_flow():
    """E2E Test: Submit chat instruction -> verify updated markdown and recapture state."""
    original_markdown = (
        "# Portal Guide\n\n"
        "## Step-by-Step Walkthrough\n"
        "### Step 1: Login\nClick the login button.\n"
    )

    # 1. Structural revision flow: user asks to add a new section
    state_revision: ManualState = {
        "job_id": "e2e-refine-002",
        "session_id": "e2e-sess-002",
        "target_url": "https://portal.example.com",
        "raw_input_script": "Login flow",
        "credentials": {},
        "structured_steps": [],
        "screenshot_assets": {},
        "markdown_content": original_markdown,
        "chat_history": [
            {
                "role": "user",
                "content": "Add section FAQ and troubleshooting notes",
            }
        ],
        "execution_logs": [],
        "quality_approved": True,
        "error_states": {},
        "quality_feedback": None,
        "quality_review_attempts": 1,
        "recapture_step_index": None,
    }

    updated_revision = await chat_refiner_node(state_revision)
    assert "FAQ and troubleshooting notes" in updated_revision["markdown_content"]
    assert any("Structural revision applied" in log for log in updated_revision["execution_logs"])

    # 2. Recapture trigger flow: user asks to re-capture step 1
    state_recapture: ManualState = {
        **state_revision,
        "chat_history": [
            {
                "role": "user",
                "content": "Please recapture the screenshot for step 1",
            }
        ],
    }

    updated_recapture = await chat_refiner_node(state_recapture)
    assert updated_recapture["recapture_step_index"] == 0
    assert any(
        "Recapture trigger set for step 0" in log for log in updated_recapture["execution_logs"]
    )


@pytest.mark.asyncio
async def test_e2e_fault_tolerance_invalid_selector():
    """E2E Test: Step with invalid selector logs error gracefully without failing generation."""
    mock_agent1 = {
        "domain": "Resilience Test",
        "steps": [
            {
                "index": 0,
                "description": "Click non-existent button",
                "action_type": "click",
                "target_selector": "button#non-existent-button-xyz-999",
                "input_value": "",
                "selector_hints": [],
            }
        ],
    }

    state: ManualState = {
        "job_id": "e2e-fault-003",
        "session_id": "e2e-sess-003",
        "target_url": "https://resilience.example.com",
        "raw_input_script": "Click missing button",
        "credentials": {},
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

    mock_compiled_md = "# Resilience Guide\n\n## Troubleshooting\nCheck missing elements.\n"
    mock_review = {
        "completeness": {"score": 85, "feedback": "OK"},
        "screenshot_coverage": {"score": 85, "feedback": "OK"},
        "tone_consistency": {"score": 85, "feedback": "OK"},
        "logical_sequencing": {"score": 85, "feedback": "OK"},
        "overall_pass": True,
        "summary": "Tolerated error successfully.",
    }

    app = create_docuagent_graph()

    with (
        patch(
            "app.agents.analyzer_agent.ollama_generate_json_with_retry", return_value=mock_agent1
        ),
        patch("app.agents.capture_agent.validate_target_url"),
        patch("app.action_dispatcher.validate_target_url"),
        patch("app.utils.url_validator.validate_target_url"),
        patch(
            "app.agents.capture_agent.inject_highlight_effects",
            side_effect=TimeoutError("Element not found"),
        ),
        patch("app.agents.capture_agent.PlaywrightCaptureEngine") as mock_engine_cls,
        patch("app.technical_writer.ollama_generate_text", return_value=mock_compiled_md),
        patch("app.quality_review.ollama_generate_json_with_retry", return_value=mock_review),
        patch("app.agents.analyzer_agent.publish_sse_event", new=AsyncMock()),
        patch("app.agents.capture_agent.publish_sse_event", new=AsyncMock()),
        patch("app.technical_writer.publish_sse_event", new=AsyncMock()),
        patch("app.quality_review.publish_sse_event", new=AsyncMock()),
    ):
        mock_engine = mock_engine_cls.return_value
        mock_engine.__aenter__ = AsyncMock(return_value=mock_engine)
        mock_engine.__aexit__ = AsyncMock(return_value=None)
        mock_engine.page = AsyncMock()
        mock_engine.context = AsyncMock()

        # Pipeline should NOT raise an unhandled exception
        final_state = await app.ainvoke(
            state,
            config={"configurable": {"thread_id": "fault-thread-001"}},
        )

    # Verifications: Error was recorded in error_states, but markdown compilation finished
    assert len(final_state["markdown_content"]) > 0
    assert "highlight_0" in final_state["error_states"]
