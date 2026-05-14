# Python modules
from typing import Any

# Django modules
from django.http import JsonResponse

# Third-party modules
import redis
from redis.exceptions import RedisError
from rest_framework.status import HTTP_429_TOO_MANY_REQUESTS

# Django modules
from django.conf import settings

# Project modules
from apps.core.middleware import get_client_ip
from settings.conf import REDIS_DB, REDIS_HOST, REDIS_PORT


MAX_REQUESTS = 100
WINDOW_SECONDS = 5 * 60
RATE_LIMIT_PATH_PREFIX = "/api/"


class RateLimitMiddleware:
    """
    IP-based rate limiting backed by Redis.

    Applies only to API routes. Uses fail-open strategy: if Redis is
    unavailable, the request passes through. Adds standard rate-limit
    headers to every response.
    """

    def __init__(self, get_response: Any) -> None:
        self.get_response = get_response
        self.redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
            socket_timeout=2,
            socket_connect_timeout=2,
        )

    def __call__(self, request: Any) -> Any:
        if getattr(settings, "DISABLE_RATE_LIMIT", False):
            return self.get_response(request)

        if not request.path.startswith(RATE_LIMIT_PATH_PREFIX):
            return self.get_response(request)

        ip = get_client_ip(request)
        if not ip:
            return self.get_response(request)

        key = f"rate_limit:{ip}"

        try:
            count = self.redis_client.incr(key)
            ttl = self.redis_client.ttl(key)
            if ttl < 0:
                self.redis_client.expire(key, WINDOW_SECONDS)
                ttl = WINDOW_SECONDS
        except RedisError:
            return self.get_response(request)

        remaining = max(0, MAX_REQUESTS - count)

        if count > MAX_REQUESTS:
            response = JsonResponse(
                {
                    "detail": "Rate limit exceeded. Try again later.",
                    "limit": MAX_REQUESTS,
                    "window_seconds": WINDOW_SECONDS,
                    "retry_after_seconds": max(ttl, 0),
                },
                status=HTTP_429_TOO_MANY_REQUESTS,
            )
            response["Retry-After"] = str(max(ttl, 0))
            response["X-RateLimit-Limit"] = str(MAX_REQUESTS)
            response["X-RateLimit-Remaining"] = "0"
            return response

        response = self.get_response(request)
        response["X-RateLimit-Limit"] = str(MAX_REQUESTS)
        response["X-RateLimit-Remaining"] = str(remaining)
        return response
