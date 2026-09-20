"""
Unit tests for app/tasks/generation_tasks.py.
Verifies generate_manual execution, job store updates, and error handling.
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.api.v1.endpoints.jobs import job_store
from app.tasks.generation_tasks import generate_manual


def test_generate_manual_success():
    job_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    job_store.create_job(job_id, session_id)

    mock_final_state = {
        "job_id": job_id,
        "session_id": session_id,
        "markdown_content": "# Generated Manual\n\nStep 1: Done.",
        "screenshot_assets": {"0": "/path/step_000.png"},
        "quality_approved": True,
    }

    with patch(
        "app.tasks.generation_tasks._execute_docuagent_workflow",
        new_callable=AsyncMock,
        return_value=mock_final_state,
    ):
        result = generate_manual(
            job_id=job_id,
            session_id=session_id,
            target_url="https://example.com",
            raw_input_script="Log in and click dashboard",
        )

        assert result["success"] is True
        assert result["markdown_content"] == mock_final_state["markdown_content"]
        assert result["quality_approved"] is True

        stored = job_store.get(job_id)
        assert stored["status"] == "completed"
        assert stored["markdown_content"] == mock_final_state["markdown_content"]


def test_generate_manual_failure_updates_store():
    job_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    job_store.create_job(job_id, session_id)

    with patch(
        "app.tasks.generation_tasks._execute_docuagent_workflow",
        new_callable=AsyncMock,
        side_effect=RuntimeError("Workflow crashed"),
    ):
        with pytest.raises(RuntimeError, match="Workflow crashed"):
            generate_manual(
                job_id=job_id,
                session_id=session_id,
                target_url="https://example.com",
            )

        stored = job_store.get(job_id)
        assert stored["status"] == "failed"
        assert "Workflow crashed" in stored["error"]
