# Django modules
from typing import Any, Callable, Optional
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.utils import translation

# Project modules
from apps.accounts.models import CustomUser


class CustomLocaleMiddleware:
    """
    Determine and activate language for each request.

    Request language priority:
    1) Authenticated user preferred_language
    2) Accept-Language header
    3) Default EN
    """

    SUPPORTED_LANGUAGES = {"en", "kk", "ru"}
    DEFAULT_LANGUAGE = "en"

    def __init__(self, get_response: Callable[[WSGIRequest], HttpResponse]) -> None:
        """Initialize the middleware with the given get_response callable."""
        self.get_response = get_response

    def __call__(self, request: WSGIRequest) -> HttpResponse:
        """Process the request to set the appropriate language."""
        lang: str = self._determine_language(request)
        translation.activate(lang)
        request.LANGUAGE_CODE = lang

        response: HttpResponse = self.get_response(request)
        response.headers.setdefault("Content-Language", lang)

        translation.deactivate()
        return response

    def _determine_language(self, request: WSGIRequest) -> str:
        """Determine the language for the request."""
        # Try to get authenticated user's preferred language
        user: Optional[Any] = getattr(request, "user", None)
        if user and getattr(user, "is_authenticated", False):
            if hasattr(user, "preferred_language") and user.preferred_language:
                normalized = self._normalize(user.preferred_language)
                if normalized:
                    return normalized

        # Try Accept-Language header
        accept_language = request.headers.get("Accept-Language", "")
        if accept_language:
            for lang_part in accept_language.split(","):
                lang_code = lang_part.split(";")[0].strip()
                normalized = self._normalize(lang_code)
                if normalized:
                    return normalized

        return self.DEFAULT_LANGUAGE

    def _normalize(self, lang: str) -> Optional[str]:
        """Normalize language code to supported languages."""
        if not lang:
            return None

        normalized = lang.lower().replace("_", "-").strip()

        # Check exact match
        if normalized in self.SUPPORTED_LANGUAGES:
            return normalized

        # Check base language (e.g., "en" from "en-US")
        base_lang = normalized.split("-")[0]
        if base_lang in self.SUPPORTED_LANGUAGES:
            return base_lang

        return None
