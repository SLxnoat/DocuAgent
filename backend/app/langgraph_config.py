"""
LangGraph configuration for DocuAgent AI.
Handles checkpointer setup for development and production environments.
"""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.redis import RedisSaver

from app.config import settings


def get_checkpointer():
    """
    Get the appropriate checkpointer based on the environment.

    Returns:
        MemorySaver for development, RedisSaver for production
    """
    if settings.app_env == "production":
        # Production: Use RedisSaver with connection from settings
        return RedisSaver.from_conn_string(
            conn_string=settings.redis_url,
            ttl=settings.asset_retention_hours * 3600,  # Convert hours to seconds
        )
    else:
        # Development/testing: Use in-memory MemorySaver
        return MemorySaver()


def get_development_checkpointer() -> MemorySaver:
    """
    Get development checkpointer using MemorySaver.

    Returns:
        MemorySaver instance for development use
    """
    return MemorySaver()


def get_production_checkpointer() -> RedisSaver | None:
    """
    Get production checkpointer using RedisSaver.

    Returns:
        RedisSaver instance for production use, or None if not configured
    """
    try:
        return RedisSaver.from_conn_string(
            conn_string=settings.redis_url,
            ttl=settings.asset_retention_hours * 3600,  # Convert hours to seconds
        )
    except Exception:
        # Fallback to memory saver if Redis is not available
        return MemorySaver()
