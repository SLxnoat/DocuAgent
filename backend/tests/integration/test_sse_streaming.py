"""
Integration tests for Server-Sent Events (SSE) streaming.
Verifies SSE endpoint validation, Redis channel pub/sub dispatch, and event streaming format.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.utils.sse_publisher import publish_sse_event


@pytest.fixture
def client():
    return TestClient(app)


def test_sse_stream_invalid_uuid(client):
    """Verify that requests with invalid UUID format return 400 Bad Request."""
    response = client.get("/api/v1/stream/invalid-uuid-1234")
    assert response.status_code == 400
    assert "Invalid job ID format" in response.json()["detail"]


@pytest.mark.asyncio
async def test_publish_sse_event_to_redis():
    """Verify that publish_sse_event serializes data and publishes to the correct Redis channel."""
    mock_redis = AsyncMock()

    with patch("app.utils.sse_publisher.get_redis_client", return_value=mock_redis):
        job_id = "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
        event_type = "step_completed"
        payload = {"step_index": 2, "status": "success"}

        await publish_sse_event(job_id=job_id, event_type=event_type, data=payload)

        # Verify Redis publish call
        expected_channel = f"docuagent:sse:{job_id}"
        mock_redis.publish.assert_awaited_once()
        call_args = mock_redis.publish.await_args[0]
        assert call_args[0] == expected_channel

        # Verify published JSON payload
        published_msg = json.loads(call_args[1])
        assert published_msg["event_type"] == event_type
        assert published_msg["data"] == payload
        assert "timestamp" in published_msg


@pytest.mark.asyncio
async def test_event_stream_generator():
    """Verify that event_stream yields SSE connection comment and formatted event messages."""
    from app.api.v1.endpoints.stream import event_stream

    job_id = "11111111-2222-3333-4444-555555555555"
    mock_request = AsyncMock()
    # First two iterations connected, third disconnected to stop generator
    mock_request.is_disconnected.side_effect = [False, False, False, True]

    mock_pubsub = AsyncMock()
    test_event_data = json.dumps({"event_type": "pipeline_started", "data": {"status": "ok"}})

    # get_message returns message on first call, None on second
    mock_pubsub.get_message.side_effect = [
        {"data": test_event_data.encode("utf-8")},
        None,
    ]

    mock_redis_client = AsyncMock()
    mock_redis_client.pubsub = MagicMock(return_value=mock_pubsub)

    with (
        patch("app.api.v1.endpoints.stream.Redis.from_url", return_value=mock_redis_client),
        patch("app.api.v1.endpoints.stream.publish_sse_event", new=AsyncMock()),
    ):
        events = []
        async for chunk in event_stream(mock_request, job_id):
            events.append(chunk)

        # Verify initial connection comment
        assert ": connected\n\n" in events

        # Verify SSE formatted data line
        data_events = [e for e in events if e.startswith("data: ")]
        assert len(data_events) >= 1
        assert "pipeline_started" in data_events[0]

        # Verify pubsub lifecycle
        mock_pubsub.subscribe.assert_awaited_once_with(f"docuagent:sse:{job_id}")
        mock_pubsub.unsubscribe.assert_awaited_once_with(f"docuagent:sse:{job_id}")
        mock_redis_client.close.assert_awaited_once()
