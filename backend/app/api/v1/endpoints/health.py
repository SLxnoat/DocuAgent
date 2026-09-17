from datetime import UTC, datetime

from fastapi import APIRouter

from app.config import settings

router = APIRouter()


@router.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint to verify the service is running.
    Returns system status, active version, and timestamp.
    """
    return {
        "status": "ok",
        "version": settings.app_version,
        "timestamp": datetime.now(UTC).isoformat(),
    }
