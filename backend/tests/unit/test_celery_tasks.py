"""
Unit tests for DocuAgent AI Celery background tasks.
Tests capture_tasks, export_tasks, maintenance_tasks, and notification_tasks.
"""

from __future__ import annotations

import uuid
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.job_store import job_store
from app.tasks.capture_tasks import recapture_step
from app.tasks.export_tasks import export_manual
from app.tasks.generation_tasks import regenerate_step
from app.tasks.maintenance_tasks import cleanup_old_assets, health_check, rotate_logs
from app.tasks.notification_tasks import send_job_completion, send_progress_update

# ------------------------------------------------------------------------------
# Capture Tasks Tests
# ------------------------------------------------------------------------------


def test_recapture_step_task_job_not_found():
    result = recapture_step(
        job_id="nonexistent-id",
        step_index=1,
    )
    assert result["success"] is False
    assert "not found" in result["error"]


def test_recapture_step_task_success(tmp_path):
    job_id = str(uuid.uuid4())
    job_store.create_job(job_id, str(uuid.uuid4()))

    with (
        patch("app.tasks.capture_tasks.settings.assets_dir", str(tmp_path)),
        patch("app.utils.sse_publisher.publish_sse_event", new_callable=AsyncMock) as mock_sse,
    ):
        result = recapture_step(
            job_id=job_id,
            step_index=2,
            selector_override="button.next",
        )
        assert result["success"] is True
        assert result["job_id"] == job_id
        assert result["step_index"] == 2
        assert Path(result["screenshot_path"]).exists()
        assert mock_sse.await_count >= 2


def test_recapture_step_task_with_custom_screenshot(tmp_path):
    job_id = str(uuid.uuid4())
    job_store.create_job(job_id, str(uuid.uuid4()))

    custom_img = tmp_path / "custom.png"
    custom_img.write_bytes(b"\x89PNGcustom")

    with (
        patch("app.tasks.capture_tasks.settings.assets_dir", str(tmp_path)),
        patch("app.utils.sse_publisher.publish_sse_event", new_callable=AsyncMock),
    ):
        result = recapture_step(
            job_id=job_id,
            step_index=1,
            custom_screenshot_path=str(custom_img),
        )
        assert result["success"] is True
        target_path = Path(result["screenshot_path"])
        assert target_path.exists()
        assert target_path.read_bytes() == b"\x89PNGcustom"


# ------------------------------------------------------------------------------
# Export Tasks Tests
# ------------------------------------------------------------------------------


def test_export_manual_job_not_found():
    result = export_manual(job_id="missing-job", fmt="markdown")
    assert result["success"] is False
    assert "not found" in result["error"]


def test_export_manual_missing_markdown():
    job_id = str(uuid.uuid4())
    job_store.create_job(job_id, str(uuid.uuid4()))
    result = export_manual(job_id=job_id, fmt="markdown")
    assert result["success"] is False
    assert "No markdown" in result["error"]


def test_export_manual_success(tmp_path):
    job_id = str(uuid.uuid4())
    job_store.create_job(job_id, str(uuid.uuid4()))
    job_store.update_job(job_id, {"markdown_content": "# Title\n\nContent"})

    out_file = tmp_path / f"manual_{job_id}.md"
    out_file.write_text("# Title\n\nContent")

    with patch("app.tasks.export_tasks.export_document", return_value=out_file):
        result = export_manual(job_id=job_id, fmt="markdown")
        assert result["success"] is True
        assert result["job_id"] == job_id
        assert result["format"] == "markdown"
        assert result["file_path"] == str(out_file)


# ------------------------------------------------------------------------------
# Maintenance Tasks Tests
# ------------------------------------------------------------------------------


def test_cleanup_old_assets(tmp_path):
    with patch("app.config.settings.assets_dir", str(tmp_path)):
        old_file = tmp_path / "old.png"
        old_file.write_text("old")
        import os
        import time

        os.utime(str(old_file), (time.time() - 100000, time.time() - 100000))

        res = cleanup_old_assets(max_age_hours=1)
        assert res["success"] is True
        assert res["files_removed"] == 1
        assert not old_file.exists()


def test_maintenance_health_check():
    with patch("redis.from_url") as mock_redis:
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        res = health_check()
        assert res["success"] is True
        assert res["redis_status"] == "healthy"
        assert "disk_status" in res


def test_maintenance_rotate_logs():
    res = rotate_logs(max_size_mb=50)
    assert res["success"] is True
    assert res["logs_rotated"] == 0


# ------------------------------------------------------------------------------
# Notification Tasks Tests
# ------------------------------------------------------------------------------


def test_send_job_completion():
    res = send_job_completion(
        job_id="job-123",
        recipient="user@example.com",
        message="Your manual is ready!",
    )
    assert res["success"] is True
    assert res["recipient"] == "user@example.com"


def test_send_progress_update():
    res = send_progress_update(
        job_id="job-123",
        step_index=2,
        progress_data={"percent": 50},
    )
    assert res["success"] is True
    assert res["step_index"] == 2


# ------------------------------------------------------------------------------
# Generation Task regenerate_step
# ------------------------------------------------------------------------------


def test_regenerate_step():
    res = regenerate_step(job_id="job-abc", step_index=3)
    assert res["success"] is True
    assert res["step_index"] == 3
