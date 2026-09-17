from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings


class BearerTokenMiddleware(BaseHTTPMiddleware):
    """
    Middleware to verify Bearer token in the Authorization header.
    """

    def __init__(self, app, exempt_paths: list | None = None):
        super().__init__(app)
        self.exempt_paths = exempt_paths or ["/health", "/docs", "/redoc", "/openapi.json"]

    async def dispatch(self, request: Request, call_next):
        # Check if the path is exempt from authentication
        if request.url.path in self.exempt_paths:
            return await call_next(request)

        # Get the Authorization header
        authorization: str = request.headers.get("Authorization")
        if not authorization:
            return JSONResponse(
                status_code=401,
                content={"detail": "Not authenticated"},
            )

        # Check if the Authorization header starts with "Bearer "
        if not authorization.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid authentication scheme"},
            )

        # Extract the token
        token = authorization[len("Bearer ") :]

        # Verify the token
        if token != settings.api_token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"},
            )

        # If token is valid, proceed with the request
        return await call_next(request)
