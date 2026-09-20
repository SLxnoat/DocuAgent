"""
Unit and integration tests for WebSocket chat endpoint (/api/v1/ws/chat/{session_id}).
Verifies compliance with DOC-004 Section 11 and frontend useWebSocket.ts contracts.
"""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from app.api.v1.endpoints.jobs import job_store
from app.main import app

client = TestClient(app, headers={"Authorization": "Bearer test-api-token-value"})


def test_websocket_invalid_session_id():
    """Verify WebSocket rejection when session_id is not a valid UUID."""
    with client.websocket_connect("/api/v1/ws/chat/invalid-uuid-format") as websocket:
        msg = websocket.receive_json()
        assert msg["type"] == "error"
        assert "Invalid session ID format" in msg["message"]


def test_websocket_ping_pong():
    """Verify keepalive ping receives immediate pong response."""
    session_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())
    job_store.create_job(job_id, session_id)

    with client.websocket_connect(f"/api/v1/ws/chat/{session_id}") as websocket:
        websocket.send_json({"type": "ping"})
        response = websocket.receive_json()
        assert response["type"] == "pong"
        assert "timestamp" in response


def test_websocket_user_message_refinement():
    """Verify user_message generates typing_start, agent_response with markdown, and typing_stop."""
    session_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())
    initial_md = "# Title\n\nInitial instructions."

    job_store.create_job(job_id, session_id)
    job_store.update_job(job_id, {"markdown_content": initial_md, "status": "awaiting_input"})

    with client.websocket_connect(f"/api/v1/ws/chat/{session_id}") as websocket:
        websocket.send_json(
            {
                "type": "user_message",
                "content": "Add a reminder to save changes regularly.",
                "timestamp": "2026-09-20T12:00:00Z",
            }
        )

        # 1. Expect typing_start indicator
        msg1 = websocket.receive_json()
        assert msg1["type"] == "typing_start"

        # 2. Expect agent_response with updated markdown
        msg2 = websocket.receive_json()
        assert msg2["type"] == "agent_response"
        assert "content" in msg2
        assert "updated_markdown" in msg2
        assert len(msg2["updated_markdown"]) > len(initial_md)
        assert msg2["recapture_triggered"] is False
        assert msg2["recapture_step_index"] is None

        # 3. Expect typing_stop indicator
        msg3 = websocket.receive_json()
        assert msg3["type"] == "typing_stop"

    # Verify document was persisted in job_store
    updated_record = job_store.get(job_id)
    assert updated_record is not None
    assert updated_record["markdown_content"] == msg2["updated_markdown"]


def test_websocket_recapture_trigger():
    """Verify recapture request over WebSocket initiates recapture signal."""
    session_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())

    job_store.create_job(job_id, session_id)
    job_store.update_job(job_id, {"markdown_content": "# Doc\nStep 1", "status": "awaiting_input"})

    with client.websocket_connect(f"/api/v1/ws/chat/{session_id}") as websocket:
        websocket.send_json(
            {
                "type": "user_message",
                "content": "Please retake screenshot for step 3",
            }
        )

        # typing_start
        msg1 = websocket.receive_json()
        assert msg1["type"] == "typing_start"

        # agent_response with recapture flags
        msg2 = websocket.receive_json()
        assert msg2["type"] == "agent_response"
        assert msg2["recapture_triggered"] is True
        assert msg2["recapture_step_index"] == 2  # 0-based for Step 3
        assert "Step 3" in msg2["content"]

        # typing_stop
        msg3 = websocket.receive_json()
        assert msg3["type"] == "typing_stop"


def test_websocket_unsupported_message_type():
    """Verify error on unknown message type."""
    session_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())
    job_store.create_job(job_id, session_id)

    with client.websocket_connect(f"/api/v1/ws/chat/{session_id}") as websocket:
        websocket.send_json({"type": "invalid_type"})
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert "Unsupported message type" in response["message"]
