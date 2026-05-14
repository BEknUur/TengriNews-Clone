from __future__ import annotations

# Python modules
import hashlib
import logging
from functools import wraps
from typing import Any, Callable

# Django modules
from django.core.cache import cache

# Third-party modules
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse

logger = logging.getLogger(__name__)

CACHE_VERSION_TTL = 60 * 60 * 24


def version_key(namespace: str) -> str:
    return f"cache:version:{namespace}"


def get_version(namespace: str) -> int:
    return cache.get(version_key(namespace), 0)


def invalidate(namespace: str) -> None:
    """Bump the version for *namespace*, making all its cached responses stale."""
    version = get_version(namespace) + 1
    cache.set(version_key(namespace), version, CACHE_VERSION_TTL)
    logger.debug("Cache invalidated: namespace=%s new_version=%s", namespace, version)


def params_hash(request: DRFRequest) -> str:
    """Stable short hash of the full query string."""
    raw = request.META.get("QUERY_STRING", "")
    return hashlib.md5(raw.encode(), usedforsecurity=False).hexdigest()[:10]


def build_key(namespace: str, version: int, *parts: Any) -> str:
    segment = ":".join(str(p) for p in parts if p != "")
    return f"cache:{namespace}:v{version}:{segment}"


def cache_response(timeout: int, namespace: str) -> Callable:
    """
    Cache a ViewSet GET action in Django's cache framework.

    - Cache key includes the *namespace* version so a single call to
      ``invalidate(namespace)`` makes all responses for that namespace stale.
    - For detail actions the key also includes the ``pk`` URL kwarg.
    - For list actions the key includes a hash of all query params so that
      different filters / pagination get separate cache entries.

    Usage::

        @cache_response(timeout=600, namespace="categories")
        def list(self, request):
            ...

        @cache_response(timeout=300, namespace="articles")
        def retrieve(self, request, pk=None):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(
            self, request: DRFRequest, *args: Any, **kwargs: Any
        ) -> DRFResponse:
            if request.method != "GET":
                return func(self, request, *args, **kwargs)

            version = get_version(namespace)
            pk = kwargs.get("pk", "")
            ph = params_hash(request) if not pk else ""
            key = build_key(namespace, version, pk, ph)

            cached = cache.get(key)
            if cached is not None:
                logger.debug("Cache HIT: key=%s", key)
                return DRFResponse(cached)

            logger.debug("Cache MISS: key=%s", key)
            response: DRFResponse = func(self, request, *args, **kwargs)

            if response.status_code == 200:
                cache.set(key, response.data, timeout)

            return response

        return wrapper

    return decorator
