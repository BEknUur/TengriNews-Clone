# Django modules
from django.http import JsonResponse

# Third-party modules
import redis
from redis.exceptions import RedisError
from rest_framework.status import HTTP_429_TOO_MANY_REQUESTS

# Project modules
from settings.conf import REDIS_DB, REDIS_HOST, REDIS_PORT


MAX_REQUESTS = 100
WINDOW_SECONDS = 5 * 60
RATE_LIMIT_PATH_PREFIX = "/api/"


class RateLimitMiddleware:
    """
    IP-based rate limiting backed by Redis.

    Notes:
        - Applies only to API routes (prefix-based).
        - Uses fail-open strategy: if Redis is unavailable, request passes through.
        - Adds standard rate-limit headers to responses.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
            socket_timeout=2,
            socket_connect_timeout=2,
        )

    def __call__(self, request):
        if not request.path.startswith(RATE_LIMIT_PATH_PREFIX):
            return self.get_response(request)

        ip = self.get_client_ip(request)
        if not ip:
            return self.get_response(request)

        key = f"rate_limit:{ip}"

        try:
            count = self.redis_client.incr(key)
            ttl = self.redis_client.ttl(key)
            if ttl == -1:
                self.redis_client.expire(key, WINDOW_SECONDS)
                ttl = WINDOW_SECONDS
            elif ttl == -2:
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

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()

        x_real_ip = request.META.get("HTTP_X_REAL_IP")
        if x_real_ip:
            return x_real_ip.strip()

        remote_addr = request.META.get("REMOTE_ADDR")
        return remote_addr.strip() if remote_addr else None
