"""
Unit tests for app/api/v1/endpoints/jobs.py.
Verifies job status retrieval, deletion, recapture dispatch, and screenshot upload.
"""

from __future__ import annotations

import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api.v1.endpoints.jobs import _cleanup_old_files, create_job_record, job_store
from app.main import app

AUTH_HEADERS = {"Authorization": "Bearer test-api-token-value"}
client = TestClient(app, headers=AUTH_HEADERS)


def test_create_job_record_helper():
    job_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    rec = create_job_record(job_id, session_id)
    assert rec["job_id"] == job_id
    assert rec["status"] == "pending"


def test_get_job_status_invalid_uuid():
    resp = client.get("/api/v1/jobs/invalid-uuid")
    assert resp.status_code == 400


def test_get_job_status_not_found():
    resp = client.get(f"/api/v1/jobs/{uuid.uuid4()}")
    assert resp.status_code == 404


def test_get_job_status_success():
    job_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    job_store.create_job(job_id, session_id)
    job_store.update_job(job_id, {"status": "completed", "progress": 100})

    resp = client.get(f"/api/v1/jobs/{job_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["job_id"] == job_id
    assert data["status"] == "completed"
    assert data["progress"] == 100


def test_delete_job_invalid_uuid():
    resp = client.delete("/api/v1/jobs/invalid-uuid")
    assert resp.status_code == 400


def test_delete_job_not_found():
    resp = client.delete(f"/api/v1/jobs/{uuid.uuid4()}")
    assert resp.status_code == 404


def test_delete_job_success_and_revokes():
    job_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    job_store.create_job(job_id, session_id)
    job_store.update_job(job_id, {"celery_task_id": "mock-task-123"})

    with patch("app.celery.celery_app.control.revoke") as mock_revoke:
        resp = client.delete(f"/api/v1/jobs/{job_id}")
        assert resp.status_code == 200
        assert resp.json()["job_id"] == job_id
        mock_revoke.assert_called_once_with("mock-task-123", terminate=True)
        assert job_id not in job_store


def test_recapture_step_invalid_uuid():
    resp = client.post("/api/v1/recapture/invalid-uuid/1")
    assert resp.status_code == 400


def test_recapture_step_not_found():
    resp = client.post(f"/api/v1/recapture/{uuid.uuid4()}/1")
    assert resp.status_code == 404


def test_recapture_step_negative_index():
    job_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    job_store.create_job(job_id, session_id)

    resp = client.post(f"/api/v1/recapture/{job_id}/-1")
    assert resp.status_code == 400


def test_recapture_step_success_202():
    job_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    job_store.create_job(job_id, session_id)

    with patch("app.tasks.capture_tasks.recapture_step.delay") as mock_delay:
        resp = client.post(
            f"/api/v1/recapture/{job_id}/2",
            json={"selector_override": "button.submit"},
        )
        assert resp.status_code == 202
        data = resp.json()
        assert data["job_id"] == job_id
        assert data["step_index"] == 2
        assert data["status"] == "recapture_queued"
        assert f"/api/v1/stream/{job_id}" in data["stream_url"]
        mock_delay.assert_called_once_with(
            job_id=job_id,
            step_index=2,
            selector_override="button.submit",
            custom_screenshot_path=None,
        )


def test_upload_screenshot_invalid_uuid():
    resp = client.post(
        "/api/v1/jobs/invalid-uuid/assets/1",
        files={"file": ("test.png", b"fake", "image/png")},
    )
    assert resp.status_code == 400


def test_upload_screenshot_not_found():
    resp = client.post(
        f"/api/v1/jobs/{uuid.uuid4()}/assets/1",
        files={"file": ("test.png", b"fake", "image/png")},
    )
    assert resp.status_code == 404


def test_upload_screenshot_negative_step():
    job_id = str(uuid.uuid4())
    job_store.create_job(job_id, str(uuid.uuid4()))
    resp = client.post(
        f"/api/v1/jobs/{job_id}/assets/-1",
        files={"file": ("test.png", b"fake", "image/png")},
    )
    assert resp.status_code == 400


def test_upload_screenshot_invalid_content_type():
    job_id = str(uuid.uuid4())
    job_store.create_job(job_id, str(uuid.uuid4()))
    resp = client.post(
        f"/api/v1/jobs/{job_id}/assets/1",
        files={"file": ("test.txt", b"fake", "text/plain")},
    )
    assert resp.status_code == 400


def test_upload_screenshot_success(tmp_path):
    job_id = str(uuid.uuid4())
    job_store.create_job(job_id, str(uuid.uuid4()))

    with patch("app.api.v1.endpoints.jobs.settings.assets_dir", str(tmp_path)):
        resp = client.post(
            f"/api/v1/jobs/{job_id}/assets/3",
            files={"file": ("step_003.png", b"\x89PNG\r\n\x1a\n", "image/png")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["job_id"] == job_id
        assert data["step_index"] == 3
        assert "step_003.png" in data["saved_path"]


def test_cleanup_old_files_helper(tmp_path):
    old_file = tmp_path / "old.txt"
    old_file.write_text("old content")
    # Set mtime to 10 days ago
    import os
    import time

    os.utime(str(old_file), (time.time() - 864000, time.time() - 864000))

    _cleanup_old_files(str(tmp_path), retention_hours=24)
    assert not old_file.exists()
