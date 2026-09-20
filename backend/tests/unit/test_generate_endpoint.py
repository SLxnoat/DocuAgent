"""
Unit tests for app/api/v1/endpoints/generate.py.
Verifies input validation, SSRF blocking, job creation, and Celery task dispatch.
"""

from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

AUTH_HEADERS = {"Authorization": "Bearer test-api-token-value"}
client = TestClient(app, headers=AUTH_HEADERS)


def test_generate_manual_ssrf_blocked():
    response = client.post(
        "/api/v1/generate",
        json={
            "target_url": "http://127.0.0.1/admin",
            "script": "Click around the local admin console",
        },
    )
    # SSRF protection must reject loopback / internal IPs with 422
    assert response.status_code == 422
    data = response.json()
    assert "error" in data["detail"]
    assert data["detail"]["error"]["code"] == "VALIDATION_ERROR"


def test_generate_manual_success_dispatches_task():
    with patch("app.tasks.generation_tasks.generate_manual.delay") as mock_task:
        response = client.post(
            "/api/v1/generate",
            json={
                "target_url": "https://example.com/login",
                "script": "Log in with admin credentials and click users",
                "credentials": {"username": "admin", "password": "password"},
            },
        )
        assert response.status_code == 202
        data = response.json()
        assert "job_id" in data
        assert "session_id" in data
        mock_task.assert_called_once()
        kwargs = mock_task.call_args[1]
        assert kwargs["job_id"] == data["job_id"]
        assert kwargs["target_url"] == "https://example.com/login"
