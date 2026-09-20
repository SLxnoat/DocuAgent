from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings


class BearerTokenMiddleware(BaseHTTPMiddleware):
    """
    Middleware to verify Bearer token in the Authorization header.

    Implements DOC-004 Section 2 / DOC-008 Section 4.1 — all API endpoints
    require ``Authorization: Bearer <api_token>`` except explicitly exempt paths.

    SSE and WebSocket upgrade paths are intentionally exempt because browsers
    cannot add custom headers to EventSource or WebSocket requests.
    """

    def __init__(
        self,
        app,
        exempt_paths: list[str] | None = None,
        exempt_prefixes: list[str] | None = None,
    ):
        super().__init__(app)
        self.exempt_paths: list[str] = exempt_paths or [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]
        self.exempt_prefixes: list[str] = exempt_prefixes or []

    def _is_exempt(self, path: str) -> bool:
        if path in self.exempt_paths:
            return True
        return any(path.startswith(prefix) for prefix in self.exempt_prefixes)

    async def dispatch(self, request: Request, call_next):
        if self._is_exempt(request.url.path):
            return await call_next(request)

        authorization: str = request.headers.get("Authorization", "")

        if not authorization:
            return JSONResponse(
                status_code=401,
                content={
                    "error": {
                        "code": "AUTHENTICATION_REQUIRED",
                        "message": "Missing Authorization header. Provide 'Authorization: Bearer <token>'.",
                        "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
                    }
                },
            )

        if not authorization.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={
                    "error": {
                        "code": "INVALID_AUTH_SCHEME",
                        "message": "Invalid authentication scheme. Expected 'Bearer <token>'.",
                        "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
                    }
                },
            )

        token = authorization[len("Bearer ") :]

        if token != settings.api_token:
            return JSONResponse(
                status_code=401,
                content={
                    "error": {
                        "code": "AUTHENTICATION_FAILED",
                        "message": "Invalid API token.",
                        "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
                    }
                },
            )

        return await call_next(request)
