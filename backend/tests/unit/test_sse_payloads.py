"""
Unit tests for SSE event payload conformance with DOC-004 Section 12.
Ensures event type, flattened fields (markdown, step_index, status, etc.),
and data dictionary match specifications required by frontend and API consumers.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest

from app.technical_writer import compile_markdown_node
from app.utils.sse_publisher import publish_sse_event


@pytest.mark.asyncio
async def test_publish_sse_event_conformance():
    """Verify that publish_sse_event flattens data and includes type and event_type."""
    mock_redis = AsyncMock()

    with patch("app.utils.sse_publisher.get_redis_client", return_value=mock_redis):
        job_id = "11111111-2222-3333-4444-555555555555"
        payload = {
            "step_index": 1,
            "total_steps": 5,
            "status": "captured",
        }

        await publish_sse_event(job_id=job_id, event_type="capture_progress", data=payload)

        mock_redis.publish.assert_awaited_once()
        channel, message_json = mock_redis.publish.await_args[0]
        assert channel == f"docuagent:sse:{job_id}"

        event = json.loads(message_json)
        assert event["type"] == "capture_progress"
        assert event["event_type"] == "capture_progress"
        assert event["step_index"] == 1
        assert event["total_steps"] == 5
        assert event["status"] == "captured"
        assert event["data"]["step_index"] == 1
        assert "timestamp" in event


@pytest.mark.asyncio
async def test_technical_writer_document_ready_has_markdown():
    """Verify that technical_writer emits document_ready with markdown content in payload."""
    published_events = []

    async def fake_publish(job_id, event_type, data):
        published_events.append((job_id, event_type, data))
        return True

    sample_markdown = "# Generated User Guide\n\nStep 1: Navigate to Dashboard."
    state = {
        "job_id": "test-job-uuid",
        "target_url": "http://localhost:3000",
        "raw_input_script": "login",
        "structured_steps": [{"action_type": "click", "target_selector": "#btn"}],
        "screenshot_assets": {0: "/path/to/step_000.png"},
        "markdown_content": "",
    }

    with (
        patch("app.technical_writer.publish_sse_event", side_effect=fake_publish),
        patch("app.technical_writer.ollama_generate_text", return_value=sample_markdown),
    ):
        result = await compile_markdown_node(state)

        assert result["markdown_content"] == sample_markdown

        # Verify document_ready was published with markdown
        doc_ready_events = [e for e in published_events if e[1] == "document_ready"]
        assert len(doc_ready_events) == 1
        event_data = doc_ready_events[0][2]
        assert "markdown" in event_data
        assert event_data["markdown"] == sample_markdown


@pytest.mark.asyncio
async def test_publish_heartbeat():
    with patch("app.utils.sse_publisher.publish_sse_event", new_callable=AsyncMock) as mock_pub:
        from app.utils.sse_publisher import publish_heartbeat

        await publish_heartbeat("job-heartbeat-uuid")
        mock_pub.assert_awaited_once_with(
            job_id="job-heartbeat-uuid",
            event_type="heartbeat",
            data={},
        )


@pytest.mark.asyncio
async def test_close_sse_redis_connections():
    import app.utils.sse_publisher as sse_pub

    mock_client = AsyncMock()
    mock_pool = AsyncMock()
    sse_pub._redis_client = mock_client
    sse_pub._redis_pool = mock_pool

    await sse_pub.close_sse_redis_connections()
    mock_client.close.assert_awaited_once()
    mock_pool.disconnect.assert_awaited_once()
    assert sse_pub._redis_client is None
    assert sse_pub._redis_pool is None
