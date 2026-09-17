from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


def setup_cors(app: FastAPI) -> None:
    """
    Set up CORS middleware with explicit allowed origins.

    Args:
        app: The FastAPI application instance.
    """
    # Parse allowed origins from settings (already parsed as list in config)
    allowed_origins = settings.allowed_origins

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
    )
