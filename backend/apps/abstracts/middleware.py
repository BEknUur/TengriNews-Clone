from __future__ import annotations

import json
import logging
import threading
import time
import uuid
import contextvars
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.utils import translation


class CustomLocaleMiddleware:
    """Determine and activate language for each request.

    Priority:
    1) Authenticated user `preferred_language` attribute
    2) `App-Language` header
    3) `Accept-Language` header
    4) Default 'en'
    """

    SUPPORTED_LANGUAGES = {"en", "ru", "kk"}
    DEFAULT_LANGUAGE = "en"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        lang = self._determine_language(request)
        translation.activate(lang)
        setattr(request, "LANGUAGE_CODE", lang)

        response = self.get_response(request)
        response.headers.setdefault("Content-Language", lang)

        translation.deactivate()
        return response

    def _determine_language(self, request: HttpRequest) -> str:
        user = getattr(request, "user", None)
        if user and getattr(user, "is_authenticated", False):
            pref = getattr(user, "preferred_language", None)
            norm = self._normalize(pref)
            if norm:
                return norm

        header_lang = request.headers.get("App-Language") or request.GET.get("lang")
        norm = self._normalize(header_lang)
        if norm:
            return norm

        accepted = request.headers.get("Accept-Language", "")
        for part in accepted.split(','):
            value = part.split(';', 1)[0].strip()
            norm = self._normalize(value)
            if norm:
                return norm

        return self.DEFAULT_LANGUAGE

    def _normalize(self, value: str | None) -> str | None:
        if not value:
            return None
        v = value.lower().replace('_', '-').strip()
        if v in self.SUPPORTED_LANGUAGES:
            return v
        base = v.split('-', 1)[0]
        if base in self.SUPPORTED_LANGUAGES:
            return base
        return None

logger = logging.getLogger("apps.requests")
_request_state = threading.local()
_request_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)


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


def set_request_id(request_id: str) -> contextvars.Token:
    """Store request_id in contextvar for the current context and return token."""
    return _request_id_ctx.set(request_id)


def get_request_id() -> str | None:
    """Return request_id from contextvar if set."""
    return _request_id_ctx.get()


def clear_request_id(token: contextvars.Token) -> None:
    _request_id_ctx.reset(token)


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


class StructuredRequestLoggingMiddleware:
    """Log request/response metadata as structured JSON."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        started_at = time.perf_counter()
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        # set request_id in context so other loggers can pick it up
        token = set_request_id(request_id)
        try:
            response = self.get_response(request)
            duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
            user = getattr(request, "user", None)
            user_id = getattr(user, "id", None) if getattr(user, "is_authenticated", False) else None

            payload: dict[str, Any] = {
                "event": "request_finished",
                "request_id": request_id,
                "method": request.method,
                "path": request.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "user_id": user_id,
                "ip": self.get_client_ip(request),
            }

            # log structured fields using extra; JsonFormatter will include extras
            logger.info("request_finished", extra=payload)
            response["X-Request-ID"] = request_id
            return response
        finally:
            clear_request_id(token)

    def get_client_ip(self, request: HttpRequest) -> str | None:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()

        x_real_ip = request.META.get("HTTP_X_REAL_IP")
        if x_real_ip:
            return x_real_ip.strip()

        remote_addr = request.META.get("REMOTE_ADDR")
        return remote_addr.strip() if remote_addr else None
