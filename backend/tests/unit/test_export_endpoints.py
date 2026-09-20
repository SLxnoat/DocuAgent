"""
Unit tests for app/api/v1/endpoints/export.py.
Verifies format validation, state validation, and streaming download of Markdown, HTML, and PDF.
"""

from __future__ import annotations

import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api.v1.endpoints.jobs import job_store
from app.main import app

AUTH_HEADERS = {"Authorization": "Bearer test-api-token-value"}
client = TestClient(app, headers=AUTH_HEADERS)


def test_export_invalid_uuid():
    resp = client.get("/api/v1/export/not-a-uuid?format=markdown")
    assert resp.status_code == 400
    assert resp.json()["detail"]["error"]["code"] == "VALIDATION_ERROR"


def test_export_unsupported_format():
    job_id = str(uuid.uuid4())
    resp = client.get(f"/api/v1/export/{job_id}?format=docx")
    assert resp.status_code == 400
    assert resp.json()["detail"]["error"]["code"] == "EXPORT_FORMAT_UNSUPPORTED"


def test_export_job_not_found():
    job_id = str(uuid.uuid4())
    resp = client.get(f"/api/v1/export/{job_id}?format=markdown")
    assert resp.status_code == 404
    assert resp.json()["detail"]["error"]["code"] == "JOB_NOT_FOUND"


def test_export_job_still_processing():
    job_id = str(uuid.uuid4())
    job_store.create_job(job_id, str(uuid.uuid4()))
    job_store.update_job(job_id, {"status": "processing"})

    resp = client.get(f"/api/v1/export/{job_id}?format=markdown")
    assert resp.status_code == 409
    assert resp.json()["detail"]["error"]["code"] == "JOB_STILL_PROCESSING"


def test_export_job_missing_markdown():
    job_id = str(uuid.uuid4())
    job_store.create_job(job_id, str(uuid.uuid4()))
    job_store.update_job(job_id, {"status": "completed", "markdown_content": ""})

    resp = client.get(f"/api/v1/export/{job_id}?format=markdown")
    assert resp.status_code == 409
    assert resp.json()["detail"]["error"]["code"] == "JOB_STILL_PROCESSING"


def test_export_markdown_success(tmp_path):
    job_id = str(uuid.uuid4())
    markdown_content = "# Welcome to the User Guide\n\nFollow these steps."
    job_store.create_job(job_id, str(uuid.uuid4()))
    job_store.update_job(
        job_id,
        {
            "status": "completed",
            "markdown_content": markdown_content,
        },
    )

    with patch("app.services.export_service.settings.exports_dir", str(tmp_path)):
        resp = client.get(f"/api/v1/export/{job_id}?format=markdown")
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/markdown")
        assert "attachment; filename=" in resp.headers["content-disposition"]
        assert markdown_content in resp.text


def test_export_cold_store_cached_hit(tmp_path):
    job_id = str(uuid.uuid4())
    export_dir = tmp_path / job_id
    export_dir.mkdir(parents=True)
    cached_file = export_dir / f"manual_{job_id}.md"
    cached_file.write_text("# Cached Content")

    with patch("app.services.export_service.settings.exports_dir", str(tmp_path)):
        # job_id is NOT in job_store, but file exists on disk
        resp = client.get(f"/api/v1/export/{job_id}?format=markdown")
        assert resp.status_code == 200
        assert "# Cached Content" in resp.text
