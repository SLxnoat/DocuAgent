"""
Redis-backed persistent job store for DocuAgent AI.
Ensures distributed multi-process memory synchronization between FastAPI and Celery workers.
Falls back gracefully to an in-memory dictionary if Redis is unreachable (e.g., during unit tests).
"""

from __future__ import annotations

import json
import logging
from datetime import date, datetime
from typing import Any

import redis

from app.config import settings

logger = logging.getLogger(__name__)


def _json_serializer(obj: Any) -> str:
    """JSON serializer for objects not serializable by default json code."""
    if isinstance(obj, datetime | date):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


class RedisJobStore:
    """
    Persistent Job Store backed by Redis (DB 0).
    Provides dictionary-like interface for transparent drop-in compatibility.
    """

    KEY_PREFIX = "docuagent:job:"
    SESSION_PREFIX = "docuagent:session:"

    def __init__(
        self,
        redis_url: str | None = None,
        ttl_hours: int | None = None,
    ):
        self.redis_url = redis_url or settings.redis_url
        self.ttl_seconds = (ttl_hours or settings.redis_ttl_hours) * 3600
        self._client: redis.Redis | None = None
        self._local_fallback: dict[str, dict[str, Any]] = {}
        self._session_fallback: dict[str, str] = {}
        self._use_fallback: bool = False

    def _get_client(self) -> redis.Redis | None:
        """Get or initialize Redis client connection."""
        if self._use_fallback:
            return None

        if self._client is not None:
            return self._client

        try:
            client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_timeout=2.0,
                socket_connect_timeout=2.0,
            )
            client.ping()
            self._client = client
            return self._client
        except Exception as exc:
            logger.debug(
                "Redis connection to %s unavailable (%s). Falling back to in-memory store.",
                self.redis_url,
                exc,
            )
            self._use_fallback = True
            return None

    def _redis_key(self, job_id: str) -> str:
        return f"{self.KEY_PREFIX}{job_id}"

    def create_job(self, job_id: str, session_id: str) -> dict[str, Any]:
        """Create a new job record with initial pending status."""
        now_iso = datetime.utcnow().isoformat()
        record: dict[str, Any] = {
            "job_id": job_id,
            "session_id": session_id,
            "status": "pending",
            "progress": 0,
            "step_statuses": [],
            "result_url": None,
            "error": None,
            "markdown_content": "",
            "screenshot_assets": {},
            "quality_approved": False,
            "created_at": now_iso,
            "updated_at": now_iso,
        }

        self.set(job_id, record)
        self.link_session(session_id, job_id)
        return record

    def link_session(self, session_id: str, job_id: str) -> None:
        """Map session_id to job_id in Redis and local store."""
        self._session_fallback[session_id] = job_id
        client = self._get_client()
        if client is not None:
            try:
                client.set(f"{self.SESSION_PREFIX}{session_id}", job_id, ex=self.ttl_seconds)
            except Exception as exc:
                logger.warning("Error linking session %s to job %s: %s", session_id, job_id, exc)

    def get_job_by_session_id(self, session_id: str) -> dict[str, Any] | None:
        """Find job record associated with a session_id."""
        job_id = None
        client = self._get_client()
        if client is not None:
            try:
                job_id = client.get(f"{self.SESSION_PREFIX}{session_id}")
            except Exception as exc:
                logger.warning("Error looking up session %s in Redis: %s", session_id, exc)

        if not job_id:
            job_id = self._session_fallback.get(session_id)

        if job_id:
            return self.get(job_id)

        # Fallback: scan local store if session_id was stored as field
        for record in self._local_fallback.values():
            if record.get("session_id") == session_id:
                return record

        # Also check if session_id itself was passed as a job_id
        return self.get(session_id)

    def get(self, job_id: str, default: Any = None) -> dict[str, Any] | None:
        """Retrieve a job record by job_id."""
        client = self._get_client()
        if client is not None:
            try:
                raw = client.get(self._redis_key(job_id))
                if raw is not None:
                    data = json.loads(raw)
                    self._local_fallback[job_id] = data
                    return data
                return default
            except Exception as exc:
                logger.warning("Error reading job %s from Redis: %s", job_id, exc)
                self._use_fallback = True

        return self._local_fallback.get(job_id, default)

    def set(self, job_id: str, data: dict[str, Any]) -> None:
        """Store or overwrite a job record."""
        self._local_fallback[job_id] = data

        client = self._get_client()
        if client is not None:
            try:
                payload = json.dumps(data, default=_json_serializer)
                client.set(self._redis_key(job_id), payload, ex=self.ttl_seconds)
            except Exception as exc:
                logger.warning("Error writing job %s to Redis: %s", job_id, exc)
                self._use_fallback = True

    def update_job(self, job_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        """Update fields in an existing job record and refresh updated_at."""
        record = self.get(job_id)
        if record is None:
            record = {"job_id": job_id}

        record.update(updates)
        record["updated_at"] = datetime.utcnow().isoformat()
        self.set(job_id, record)
        return record

    def delete(self, job_id: str) -> bool:
        """Remove a job record from Redis and local fallback."""
        deleted = False
        if job_id in self._local_fallback:
            del self._local_fallback[job_id]
            deleted = True

        client = self._get_client()
        if client is not None:
            try:
                res = client.delete(self._redis_key(job_id))
                if res > 0:
                    deleted = True
            except Exception as exc:
                logger.warning("Error deleting job %s from Redis: %s", job_id, exc)

        return deleted

    def exists(self, job_id: str) -> bool:
        """Check if job exists."""
        client = self._get_client()
        if client is not None:
            try:
                return bool(client.exists(self._redis_key(job_id)))
            except Exception as exc:
                logger.warning("Error checking job %s existence in Redis: %s", job_id, exc)
                self._use_fallback = True

        return job_id in self._local_fallback

    # ── Mapping protocol for drop-in dict compatibility ─────────────────────

    def __getitem__(self, job_id: str) -> dict[str, Any]:
        record = self.get(job_id)
        if record is None:
            raise KeyError(job_id)
        return record

    def __setitem__(self, job_id: str, data: dict[str, Any]) -> None:
        self.set(job_id, data)

    def __delitem__(self, job_id: str) -> None:
        if not self.exists(job_id):
            raise KeyError(job_id)
        self.delete(job_id)

    def __contains__(self, job_id: str) -> bool:
        return self.exists(job_id)


# Global singleton instance of RedisJobStore
job_store = RedisJobStore()
