import json
import logging
import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.logging import SensitiveDataFilter


class JSONLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log requests and responses in structured JSON format.
    """

    def __init__(self, app, logger_name: str = "request_logger"):
        super().__init__(app)
        self.logger = logging.getLogger(logger_name)
        # Add the SensitiveDataFilter to the logger if not already present
        if not any(isinstance(f, SensitiveDataFilter) for f in self.logger.filters):
            self.logger.addFilter(SensitiveDataFilter())

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate a unique request ID
        request_id = str(uuid.uuid4())
        # Add request ID to the request state for potential use in endpoints
        request.state.request_id = request_id

        # Log the request
        self._log_request(request, request_id)

        # Process the request and get the response
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        # Log the response
        self._log_response(request, response, request_id, process_time)

        return response

    def _log_request(self, request: Request, request_id: str) -> None:
        """
        Log the incoming request.

        Args:
            request: The incoming request.
            request_id: The unique request ID.
        """
        message = (
            f"Request started: {request.method} {request.url.path}?{request.url.query}"
            if request.url.query
            else ""
        )
        log_entry = {
            "timestamp": self._get_timestamp(),
            "level": "INFO",
            "request_id": request_id,
            "message": message.strip(),
        }
        self.logger.info(json.dumps(log_entry))

    def _log_response(
        self, request: Request, response: Response, request_id: str, process_time: float
    ) -> None:
        """
        Log the outgoing response.

        Args:
            request: The incoming request.
            response: The outgoing response.
            request_id: The unique request ID.
            process_time: The time taken to process the request in seconds.
        """
        message = (
            f"Request completed: {request.method} {request.url.path}"
            f" - Status: {response.status_code} - Duration: {process_time:.3f}s"
        )
        log_entry = {
            "timestamp": self._get_timestamp(),
            "level": "INFO",
            "request_id": request_id,
            "message": message,
        }
        self.logger.info(json.dumps(log_entry))

    @staticmethod
    def _get_timestamp() -> str:
        """
        Get the current timestamp in ISO 8601 format.

        Returns:
            Current timestamp as a string in ISO 8601 format.
        """
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
