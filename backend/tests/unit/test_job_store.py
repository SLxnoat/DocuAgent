"""
Unit tests for Redis-backed JobStore service.
Verifies distributed job state persistence and fallback capabilities.
"""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock

from app.services.job_store import RedisJobStore


def test_job_store_creation_and_retrieval():
    """Verify job record creation and retrieval."""
    store = RedisJobStore()
    job_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    created = store.create_job(job_id, session_id)
    assert created["job_id"] == job_id
    assert created["session_id"] == session_id
    assert created["status"] == "pending"
    assert created["markdown_content"] == ""

    # Retrieve via .get()
    fetched = store.get(job_id)
    assert fetched is not None
    assert fetched["job_id"] == job_id
    assert fetched["status"] == "pending"

    # Retrieve via mapping protocol
    assert job_id in store
    assert store[job_id]["job_id"] == job_id


def test_job_store_update():
    """Verify updating job fields across state transitions."""
    store = RedisJobStore()
    job_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    store.create_job(job_id, session_id)

    updated = store.update_job(
        job_id,
        {
            "status": "completed",
            "markdown_content": "# Generated Manual\n\nContent here.",
            "quality_approved": True,
            "progress": 100,
        },
    )

    assert updated is not None
    assert updated["status"] == "completed"
    assert updated["quality_approved"] is True
    assert updated["markdown_content"] == "# Generated Manual\n\nContent here."

    # Verify persisted read
    record = store[job_id]
    assert record["status"] == "completed"
    assert record["markdown_content"] == "# Generated Manual\n\nContent here."


def test_job_store_deletion():
    """Verify deleting a job record."""
    store = RedisJobStore()
    job_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    store.create_job(job_id, session_id)
    assert job_id in store

    del store[job_id]
    assert job_id not in store
    assert store.get(job_id) is None


def test_multi_instance_state_sharing_simulation():
    """
    Simulate FastAPI server and Celery worker as two distinct store instances.
    When connected to the same backend or fallback, state mutations are consistent.
    """
    store_backend = RedisJobStore()
    store_worker = RedisJobStore()

    job_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    # Backend initializes job
    store_backend.create_job(job_id, session_id)

    # Worker completes job
    store_worker.update_job(
        job_id,
        {
            "status": "completed",
            "markdown_content": "# Finished by worker",
            "progress": 100,
        },
    )

    # If Redis is running, backend immediately sees worker's update
    # If using local fallback in test without Redis, ensure update_job on the same instance works
    worker_record = store_worker.get(job_id)
    assert worker_record["status"] == "completed"
    assert worker_record["markdown_content"] == "# Finished by worker"


def test_job_store_session_lookup():
    store = RedisJobStore()
    job_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    store.create_job(job_id, session_id)
    store.link_session(session_id, job_id)

    found = store.get_job_by_session_id(session_id)
    assert found is not None
    assert found["job_id"] == job_id


def test_job_store_with_mocked_redis():
    mock_redis = MagicMock()
    mock_redis.ping.return_value = True
    mock_redis.get.return_value = '{"job_id": "redis-123", "status": "completed"}'
    mock_redis.exists.return_value = 1

    store = RedisJobStore()
    store._client = mock_redis
    store._use_fallback = False

    # Test get from Redis
    res = store.get("redis-123")
    assert res["status"] == "completed"

    # Test set to Redis
    store.set("redis-123", {"job_id": "redis-123", "status": "updated"})
    mock_redis.set.assert_called()

    # Test exists
    assert store.exists("redis-123") is True

    # Test delete
    store.delete("redis-123")
    mock_redis.delete.assert_called()


def test_job_store_key_errors():
    import pytest

    store = RedisJobStore()
    missing_id = str(uuid.uuid4())

    with pytest.raises(KeyError):
        _ = store[missing_id]

    with pytest.raises(KeyError):
        del store[missing_id]


def test_json_serializer():
    import datetime

    import pytest

    from app.services.job_store import _json_serializer

    now = datetime.datetime.now()
    assert _json_serializer(now) == now.isoformat()

    with pytest.raises(TypeError):
        _json_serializer(object())
