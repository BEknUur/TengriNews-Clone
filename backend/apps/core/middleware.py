from __future__ import annotations

# Python modules
import json
import logging
import threading
import time
import uuid
from typing import Any

# Django modules
from django.http import HttpRequest, HttpResponse

logger = logging.getLogger("apps.requests")
request_state = threading.local()


def get_client_ip(request: Any) -> str | None:
    """Extract the real client IP from request headers."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    x_real_ip = request.META.get("HTTP_X_REAL_IP")
    if x_real_ip:
        return x_real_ip.strip()
    remote_addr = request.META.get("REMOTE_ADDR")
    return remote_addr.strip() if remote_addr else None


def get_current_user() -> Any:
    """Return user from the current request thread, if available."""
    return getattr(request_state, "user", None)


def set_current_user(user: Any) -> None:
    """Store current request user for signal handlers."""
    request_state.user = user


def clear_current_user() -> None:
    """Clear request-local user after response."""
    if hasattr(request_state, "user"):
        delattr(request_state, "user")


class CurrentUserMiddleware:
    """Expose request.user to model signal handlers in the current thread."""

    def __init__(self, get_response: Any) -> None:
        """Initialize instance."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process the incoming request and return the resulting response."""
        user = getattr(request, "user", None)
        set_current_user(user if getattr(user, "is_authenticated", False) else None)
        try:
            return self.get_response(request)
        finally:
            clear_current_user()


class StructuredRequestLoggingMiddleware:
    """Log request/response metadata as structured JSON."""

    def __init__(self, get_response: Any) -> None:
        """Initialize instance."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process the incoming request and return the resulting response."""
        started_at = time.perf_counter()
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        response = self.get_response(request)

        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        user = getattr(request, "user", None)
        user_id = (
            getattr(user, "id", None)
            if getattr(user, "is_authenticated", False)
            else None
        )

        payload: dict[str, Any] = {
            "event": "request_finished",
            "request_id": request_id,
            "method": request.method,
            "path": request.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "user_id": user_id,
            "ip": get_client_ip(request),
        }

        logger.info(json.dumps(payload, ensure_ascii=False))
        response["X-Request-ID"] = request_id
        return response
