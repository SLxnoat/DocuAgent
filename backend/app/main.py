from fastapi import FastAPI

from app.api.v1.endpoints.generate import router as generate_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.jobs import router as jobs_router
from app.api.v1.endpoints.stream import router as stream_router
from app.api.v1.endpoints.websocket import router as websocket_router

app = FastAPI(title="DocuAgent AI", version="1.0.0")

# Include routers
app.include_router(health_router)
app.include_router(generate_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(stream_router, prefix="/api/v1")
app.include_router(websocket_router, prefix="/api/v1")

# TODO: Include other routers (chat, export, etc.)
