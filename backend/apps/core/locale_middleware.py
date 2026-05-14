from __future__ import annotations

# Python modules
from typing import Any, Callable

# Django modules
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.utils import translation


class CustomLocaleMiddleware:
    """
    Activate the correct language for each request.

    Priority:
    1. Authenticated user's preferred_language field
    2. App-Language request header
    3. Accept-Language request header
    4. Default: English
    """

    SUPPORTED_LANGUAGES = {"en", "kk", "ru"}
    DEFAULT_LANGUAGE = "en"

    def __init__(self, get_response: Callable[[WSGIRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: WSGIRequest) -> HttpResponse:
        lang = self._resolve_language(request)
        translation.activate(lang)
        request.LANGUAGE_CODE = lang

        response = self.get_response(request)
        response.headers.setdefault("Content-Language", lang)
        translation.deactivate()
        return response

    def _resolve_language(self, request: WSGIRequest) -> str:
        """Return the best matching supported language for the request."""
        user: Any = getattr(request, "user", None)
        if user and getattr(user, "is_authenticated", False):
            lang = self._normalize(getattr(user, "preferred_language", ""))
            if lang:
                return lang

        lang = self._normalize(
            request.headers.get("App-Language") or request.GET.get("lang")
        )
        if lang:
            return lang

        for part in request.headers.get("Accept-Language", "").split(","):
            lang = self._normalize(part.split(";")[0].strip())
            if lang:
                return lang

        return self.DEFAULT_LANGUAGE

    def _normalize(self, lang: str | None) -> str | None:
        """Map a raw language tag to a supported code, or None."""
        if not lang:
            return None
        base = lang.lower().replace("_", "-").split("-")[0].strip()
        return base if base in self.SUPPORTED_LANGUAGES else None
