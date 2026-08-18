from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.celery_app import celery_app
from app.config.settings import settings
from app.utils.logger import logger


class BrokerAvailabilityMiddleware(BaseHTTPMiddleware):
    """Middleware to ensure broker is available for queue operations."""

    # Endpoints that require broker availability
    QUEUE_DEPENDENT_ENDPOINTS = [
        "/api/cv/add",
        "/api/cv/update",
    ]

    def _is_broker_dependent_request(self, request: Request) -> bool:
        """Check if the request path depends on broker availability."""
        return any(
            request.url.path.startswith(endpoint)
            for endpoint in self.QUEUE_DEPENDENT_ENDPOINTS
        )

    def _check_broker_availability(self) -> bool:
        """Verify broker is available and can be connected to."""
        if not celery_app:
            logger.error("Celery app is not configured")
            return False

        try:
            connection = celery_app.connection_for_write()
            connection.connect_timeout = settings.celery_broker_connection_timeout
            connection.ensure_connection(
                max_retries=settings.celery_broker_connection_max_retries,
            )
            connection.release()
            return True
        except Exception as exc:
            logger.error(f"Broker availability check failed: {exc}")
            return False

    async def dispatch(self, request: Request, call_next):
        """Check broker availability before processing queue-dependent requests."""
        if self._is_broker_dependent_request(request):
            if not self._check_broker_availability():
                logger.warning(
                    f"Broker unavailable for request: {request.method} {request.url.path}"
                )
                return JSONResponse(
                    status_code=503,
                    content={
                        "error": "Service Unavailable",
                        "detail": "Message broker is currently unavailable. Please try again later.",
                    },
                )

        return await call_next(request)
