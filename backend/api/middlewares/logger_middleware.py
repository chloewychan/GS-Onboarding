import time
from datetime import datetime
from typing import Any, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Example: replace this with your custom logger
# from app.logging import logger
from backend.utils.logging import logger


class LoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Response:
        start_time = time.perf_counter()
        request_time = datetime.utcnow().isoformat()

        method = request.method
        url = str(request.url)
        query_params = dict(request.query_params)
        client_ip = request.client.host if request.client else "unknown"

        logger.info(
            "Incoming request",
            extra={
                "method": method,
                "url": url,
                "query_params": query_params,
                "client_ip": client_ip,
                "timestamp": request_time,
            },
        )

        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

            logger.exception(
                "Request failed",
                extra={
                    "method": method,
                    "url": url,
                    "duration_ms": duration_ms,
                },
            )
            raise exc

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        logger.info(
            "Outgoing response",
            extra={
                "method": method,
                "url": url,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )

        return response
