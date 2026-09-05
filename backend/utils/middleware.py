"""Request middleware: request ID injection, logging, error handling."""

import uuid
import time
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger("docshield")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Inject a unique request_id into each request for correlation."""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start_time = time.time()

        try:
            response = await call_next(request)
            duration = time.time() - start_time
            response.headers["X-Request-ID"] = request_id
            logger.info(
                f"[{request_id}] {request.method} {request.url.path} "
                f"-> {response.status_code} ({duration:.3f}s)"
            )
            return response
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"[{request_id}] {request.method} {request.url.path} "
                f"-> 500 ({duration:.3f}s) ERROR: {str(e)}"
            )
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An internal error occurred",
                        "retryable": False,
                    },
                    "request_id": request_id,
                },
            )
