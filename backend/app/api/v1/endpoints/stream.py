"""
Server-Sent Events (SSE) endpoint for DocuAgent AI.
Provides real-time progress streaming for jobs.
"""

import asyncio
import contextlib
import json
import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from redis.asyncio import Redis

from app.config import settings
from app.models import is_valid_uuid
from app.utils.sse_publisher import publish_sse_event

logger = logging.getLogger(__name__)

router = APIRouter()


async def event_stream(request: Request, job_id: str) -> AsyncGenerator[str, None]:
    """
    Generate SSE events for a specific job by subscribing to Redis channel.

    Args:
        request: FastAPI request object
        job_id: Unique identifier for the job

    Yields:
        SSE formatted strings
    """
    # Create a Redis client for subscribing
    redis_client = Redis.from_url(settings.redis_pubsub_url)
    pubsub = redis_client.pubsub()

    try:
        # Subscribe to the job's SSE channel
        channel = f"docuagent:sse:{job_id}"
        await pubsub.subscribe(channel)

        logger.info("Subscribed to SSE channel: %s for job_id: %s", channel, job_id)

        # Send a comment to establish connection (optional)
        yield ": connected\n\n"

        # Heartbeat task
        async def send_heartbeat():
            while True:
                try:
                    # Check if the client is still connected
                    if await request.is_disconnected():
                        break
                    # Publish a heartbeat event
                    await publish_sse_event(job_id, "heartbeat", {})
                    # Wait 15 seconds before next heartbeat
                    await asyncio.sleep(15)
                except Exception as e:
                    logger.error("Error sending heartbeat: %s", e)
                    break

        # Start the heartbeat task
        heartbeat_task = asyncio.create_task(send_heartbeat())

        try:
            # Listen for messages from the Redis channel
            while True:
                # Check if the client is still connected
                if await request.is_disconnected():
                    break

                # Get a message from the pubsub (with timeout to allow checking connection)
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    # The message data is bytes, we need to decode it
                    data = message["data"]
                    if isinstance(data, bytes):
                        data = data.decode("utf-8")
                    # The data is a JSON string we published
                    # We'll yield it as an SSE event
                    yield f"data: {data}\n\n"
                else:
                    # No message, sleep briefly to avoid busy loop
                    await asyncio.sleep(0.1)
        finally:
            # Cancel the heartbeat task
            heartbeat_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await heartbeat_task

    except Exception as e:
        logger.error("Error in SSE stream for job_id %s: %s", job_id, e)
        # Yield an error event
        yield f"data: {json.dumps({'event_type': 'error', 'data': {'message': str(e)}, 'timestamp': ''})}\n\n"
    finally:
        # Clean up
        await pubsub.unsubscribe(channel)
        await redis_client.close()
        logger.info("Unsubscribed from SSE channel: %s for job_id: %s", channel, job_id)


@router.get("/stream/{job_id}")
async def stream_job_progress(request: Request, job_id: str):
    """
    Server-Sent Events endpoint for job progress streaming.

    Args:
        request: FastAPI request object
        job_id: Unique identifier for the job

    Returns:
        StreamingResponse: SSE stream of job progress events
    """
    if not is_valid_uuid(job_id):
        raise HTTPException(status_code=400, detail="Invalid job ID format. Must be UUIDv4.")

    return StreamingResponse(
        event_stream(request, job_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
        },
    )
