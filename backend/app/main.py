from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles

from app.api.v1.endpoints.chat import router as chat_router
from app.api.v1.endpoints.export import router as export_router
from app.api.v1.endpoints.generate import router as generate_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.jobs import router as jobs_router
from app.api.v1.endpoints.models import router as models_router
from app.api.v1.endpoints.stream import router as stream_router
from app.api.v1.endpoints.websocket import router as websocket_router
from app.config import settings
from app.middleware.auth import BearerTokenMiddleware
from app.middleware.cors import setup_cors
from app.middleware.logging_middleware import JSONLoggingMiddleware
from app.middleware.rate_limit import setup_rate_limiting

app = FastAPI(title=settings.app_name, version=settings.app_version)

# Setup Middlewares (order matters — middlewares are applied in LIFO order)
setup_cors(app)
setup_rate_limiting(app)
app.add_middleware(JSONLoggingMiddleware)
# DOC-004 Section 2 / DOC-008 Section 4.1: Bearer token required on all API routes.
# SSE and WebSocket paths are exempt because the browser EventSource / WebSocket APIs
# cannot set the Authorization header — token validation is handled at the socket
# upgrade/query-param level in those handlers when needed.
app.add_middleware(
    BearerTokenMiddleware,
    exempt_paths=[
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/metrics",
    ],
    exempt_prefixes=[
        "/api/v1/stream/",  # EventSource — cannot send headers
        "/api/v1/ws/",  # WebSocket upgrade — cannot send headers
        "/assets/",  # Static files — no sensitive data
    ],
)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next) -> Response:  # type: ignore[type-arg]
    """
    Enforce hardened HTTP response headers for protection against XSS, clickjacking,
    MIME sniffing, and unauthorized caching of sensitive API data.
    """
    response: Response = await call_next(request)

    # Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"

    # Path-specific Cache Control
    if request.url.path.startswith("/assets/"):
        response.headers["Cache-Control"] = "public, max-age=3600, immutable"
    elif request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"

    return response


# Include routers
app.include_router(health_router)
app.include_router(generate_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(models_router, prefix="/api/v1")
app.include_router(stream_router, prefix="/api/v1")
app.include_router(websocket_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(export_router, prefix="/api/v1")

# Ensure and mount static assets directory
assets_path = Path(settings.assets_dir).resolve()
assets_path.mkdir(parents=True, exist_ok=True)
app.mount("/assets", StaticFiles(directory=str(assets_path)), name="assets")

# Prometheus Metrics Instrumentation
try:
    from prometheus_fastapi_instrumentator import Instrumentator

    Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        should_respect_env_var=False,
    ).instrument(app).expose(app, endpoint="/metrics", tags=["monitoring"])
except ImportError:
    pass
