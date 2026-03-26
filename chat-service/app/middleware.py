from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
import logging
import uuid

logger = logging.getLogger(__name__)

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get or generate Request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Add request_id to request state for use in endpoints
        request.state.request_id = request_id

        # Log with Request ID
        logger.info(f"[{request_id}] {request.method} {request.url.path}")

        # Process request
        response = await call_next(request)

        # Add Request ID to response
        response.headers["X-Request-ID"] = request_id

        # Log response
        logger.info(f"[{request_id}] {request.method} {request.url.path} - {response.status_code}")

        return response
