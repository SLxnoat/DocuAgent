"""
Unit tests for BearerTokenMiddleware.
Verifies DOC-004 Section 2 / DOC-008 Section 4.1 authentication enforcement:
- Missing Authorization header → 401 AUTHENTICATION_REQUIRED
- Wrong scheme (Basic, etc.) → 401 INVALID_AUTH_SCHEME
- Wrong token → 401 AUTHENTICATION_FAILED
- Exempt paths are accessible without auth
- Valid token allows request through
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

AUTH_HEADERS = {"Authorization": "Bearer test-api-token-value"}
client_authed = TestClient(app, headers=AUTH_HEADERS)
client_no_auth = TestClient(app, raise_server_exceptions=False)


def test_protected_route_no_auth():
    """Any /api/v1/* route should return 401 if Authorization header is missing."""
    response = client_no_auth.post(
        "/api/v1/chat/00000000-0000-0000-0000-000000000001",
        json={"message": "hello"},
    )
    assert response.status_code == 401
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == "AUTHENTICATION_REQUIRED"


def test_protected_route_wrong_scheme():
    """Basic auth scheme should return 401 INVALID_AUTH_SCHEME."""
    response = client_no_auth.post(
        "/api/v1/chat/00000000-0000-0000-0000-000000000001",
        json={"message": "hello"},
        headers={"Authorization": "Basic dXNlcjpwYXNz"},
    )
    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "INVALID_AUTH_SCHEME"


def test_protected_route_wrong_token():
    """Wrong token value should return 401 AUTHENTICATION_FAILED."""
    response = client_no_auth.post(
        "/api/v1/chat/00000000-0000-0000-0000-000000000001",
        json={"message": "hello"},
        headers={"Authorization": "Bearer definitely-wrong-token"},
    )
    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "AUTHENTICATION_FAILED"


def test_health_exempt_no_auth():
    """Health endpoint is exempt and should return 200 without auth."""
    response = client_no_auth.get("/health")
    assert response.status_code == 200


def test_sse_stream_exempt_no_auth():
    """SSE stream path is exempt (EventSource cannot set headers)."""
    # Will get 400 for invalid UUID, not 401 — proving auth middleware was skipped
    response = client_no_auth.get("/api/v1/stream/not-a-valid-uuid")
    assert response.status_code == 400
    assert "Invalid job ID format" in response.json()["detail"]


def test_valid_token_passes():
    """A request with the correct Bearer token should reach the endpoint."""
    # Will get 400 (invalid UUID) or 404 — anything other than 401
    response = client_authed.post(
        "/api/v1/chat/not-a-valid-uuid",
        json={"message": "hello"},
    )
    # 400 means auth passed, endpoint validation kicked in
    assert response.status_code == 400
    assert response.json()["detail"]["error"]["code"] == "VALIDATION_ERROR"
