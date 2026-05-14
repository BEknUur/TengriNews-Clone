from __future__ import annotations

import threading

from django.http import HttpRequest, HttpResponse

_request_state = threading.local()


def get_current_user():
    """Return user from the current request thread, if available."""
    return getattr(_request_state, "user", None)


def set_current_user(user) -> None:
    """Store current request user for signal handlers."""
    _request_state.user = user


def clear_current_user() -> None:
    """Clear request-local user after response."""
    if hasattr(_request_state, "user"):
        delattr(_request_state, "user")


class CurrentUserMiddleware:
    """Expose request.user to model signal handlers in the current thread."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        user = getattr(request, "user", None)
        set_current_user(user if getattr(user, "is_authenticated", False) else None)
        try:
            return self.get_response(request)
        finally:
            clear_current_user()
