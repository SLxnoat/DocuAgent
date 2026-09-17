"""
Server-Sent Events (SSE) publisher utility for DocuAgent AI.
Publishes events to Redis channels for SSE streaming.
"""

import json
import logging
from typing import Any

import redis.asyncio as redis

from app.config import settings

logger = logging.getLogger(__name__)

# Global Redis connection pool for SSE
_redis_pool: redis.ConnectionPool | None = None
_redis_client: redis.Redis | None = None


async def get_redis_client() -> redis.Redis:
    """
    Get or create a Redis client connection for SSE.

    Returns:
        Redis client instance
    """
    global _redis_client, _redis_pool

    if _redis_client is None:
        try:
            _redis_pool = redis.ConnectionPool.from_url(settings.redis_pubsub_url)
            _redis_client = redis.Redis(connection_pool=_redis_pool)
            # Test the connection
            await _redis_client.ping()
            logger.info("Connected to Redis for SSE at %s", settings.redis_pubsub_url)
        except Exception as e:
            logger.error("Failed to connect to Redis for SSE: %s", e)
            # Return a dummy client that won't actually publish
            _redis_client = redis.Redis()  # This will fail on actual operations but we'll handle it

    return _redis_client


async def publish_sse_event(
    job_id: str, event_type: str, data: dict[str, Any] | None = None
) -> bool:
    """
    Publish an SSE event to Redis channel for a specific job.

    Args:
        job_id: Unique identifier for the job
        event_type: Type of event (e.g., 'pipeline_started', 'script_analyzed')
        data: Additional data to include in the event

    Returns:
        bool: True if published successfully, False otherwise
    """
    if data is None:
        data = {}

    try:
        redis_client = await get_redis_client()

        # Create the event payload
        event = {
            "event_type": event_type,
            "data": data,
            "timestamp": str(__import__("datetime").datetime.now().isoformat()),
        }

        # Publish to the job-specific SSE channel
        channel = f"docuagent:sse:{job_id}"
        message = json.dumps(event)

        # Publish the message
        await redis_client.publish(channel, message)

        logger.debug(
            "Published SSE event to %s: job_id=%s, event_type=%s", channel, job_id, event_type
        )

        return True

    except Exception as e:
        logger.error(
            "Failed to publish SSE event: job_id=%s, event_type=%s, error=%s", job_id, event_type, e
        )
        return False


async def publish_heartbeat(job_id: str) -> bool:
    """
    Publish a heartbeat event to keep the SSE connection alive.

    Args:
        job_id: Unique identifier for the job

    Returns:
        bool: True if published successfully, False otherwise
    """
    return await publish_sse_event(job_id=job_id, event_type="heartbeat", data={})


async def close_sse_redis_connections() -> None:
    """
    Close Redis connections and clean up resources for SSE.
    """
    global _redis_client, _redis_pool

    try:
        if _redis_client:
            await _redis_client.close()
            _redis_client = None
        if _redis_pool:
            await _redis_pool.disconnect()
            _redis_pool = None
        logger.info("Closed SSE Redis connections")
    except Exception as e:
        logger.error("Error closing SSE Redis connections: %s", e)
