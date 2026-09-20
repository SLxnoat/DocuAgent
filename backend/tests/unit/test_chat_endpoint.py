"""
Unit and integration tests for POST /api/v1/chat/{session_id} endpoint.
Verifies compliance with DOC-004 Section 7 specifications.
"""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from app.api.v1.endpoints.jobs import job_store
from app.main import app

client = TestClient(app, headers={"Authorization": "Bearer test-api-token-value"})


def test_chat_endpoint_invalid_session_id():
    """Verify 400 Bad Request on malformed session ID."""
    response = client.post(
        "/api/v1/chat/not-a-valid-uuid",
        json={"message": "Please add a note to step 1."},
    )
    assert response.status_code == 400
    data = response.json()
    assert "error" in data["detail"]
    assert data["detail"]["error"]["code"] == "VALIDATION_ERROR"


def test_chat_endpoint_session_not_found():
    """Verify 404 Not Found when session does not exist in store."""
    random_session_id = str(uuid.uuid4())
    response = client.post(
        f"/api/v1/chat/{random_session_id}",
        json={"message": "Update the introduction."},
    )
    assert response.status_code == 404
    data = response.json()
    assert "error" in data["detail"]
    assert data["detail"]["error"]["code"] == "SESSION_NOT_FOUND"


def test_chat_endpoint_text_refinement():
    """Verify successful text refinement and markdown update."""
    job_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    initial_markdown = "# User Manual\n\n## Step 1: Login\nEnter your username."
    job_store.create_job(job_id, session_id)
    job_store.update_job(
        job_id,
        {
            "markdown_content": initial_markdown,
            "status": "awaiting_input",
        },
    )

    response = client.post(
        f"/api/v1/chat/{session_id}",
        json={
            "message": "Add a warning note about case-sensitive passwords",
            "context": {
                "current_markdown": initial_markdown,
            },
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert "response_message" in data
    assert "updated_markdown" in data
    assert len(data["updated_markdown"]) > len(initial_markdown)
    assert data["recapture_triggered"] is False
    assert data["recapture_step_index"] is None
    assert len(data["changes_summary"]) > 0

    # Verify update persisted in job_store
    persisted = job_store.get(job_id)
    assert persisted is not None
    assert persisted["markdown_content"] == data["updated_markdown"]


def test_chat_endpoint_recapture_trigger():
    """Verify screenshot recapture triggering from conversational request."""
    job_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    job_store.create_job(job_id, session_id)
    job_store.update_job(
        job_id,
        {
            "markdown_content": "# Manual\n## Step 2\nClick submit.",
            "status": "awaiting_input",
        },
    )

    response = client.post(
        f"/api/v1/chat/{session_id}",
        json={
            "message": "Please retake screenshot for step 2",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert data["recapture_triggered"] is True
    assert data["recapture_step_index"] == 1  # 0-based index for Step 2
    assert "Step 2" in data["response_message"]

    # Verify job record updated
    persisted = job_store.get(job_id)
    assert persisted is not None
    assert persisted["recapture_step_index"] == 1
