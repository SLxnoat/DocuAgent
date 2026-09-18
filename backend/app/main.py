from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.v1.endpoints.generate import router as generate_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.jobs import router as jobs_router
from app.api.v1.endpoints.stream import router as stream_router
from app.api.v1.endpoints.websocket import router as websocket_router
from app.config import settings
from app.middleware.cors import setup_cors
from app.middleware.logging_middleware import JSONLoggingMiddleware
from app.middleware.rate_limit import setup_rate_limiting

app = FastAPI(title=settings.app_name, version=settings.app_version)

# Setup Middlewares
setup_cors(app)
setup_rate_limiting(app)
app.add_middleware(JSONLoggingMiddleware)

# Include routers
app.include_router(health_router)
app.include_router(generate_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(stream_router, prefix="/api/v1")
app.include_router(websocket_router, prefix="/api/v1")

# Ensure and mount static assets directory
assets_path = Path(settings.assets_dir).resolve()
assets_path.mkdir(parents=True, exist_ok=True)
app.mount("/assets", StaticFiles(directory=str(assets_path)), name="assets")
