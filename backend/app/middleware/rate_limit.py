from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address


def setup_rate_limiting(app: FastAPI) -> None:
    """
    Set up rate limiting using slowapi.

    Args:
        app: The FastAPI application instance.
    """
    # Create a limiter instance
    # Using IP address as the key function
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["100/minute"],  # Default limit for all routes
        # We'll override specific limits in the route decorators
    )

    # Attach the limiter to the app state so it can be accessed in routes
    app.state.limiter = limiter

    # Add the SlowAPI middleware to handle rate limiting
    app.add_middleware(SlowAPIMiddleware)

    # Add a custom exception handler for rate limit exceeded
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={"detail": f"Rate limit exceeded: {exc.detail}"},
        )


# Example usage in a route (to be placed in the route definition file):
# from fastapi import APIRouter
# from app.main import app  # or wherever the app instance is
#
# router = APIRouter()
#
# @router.post("/generate")
# @app.state.limiter.limit("5/minute")  # Allow 5 requests per minute per IP
# async def generate_endpoint():
#     return {"message": "Generation started"}
#
# app.include_router(router)
