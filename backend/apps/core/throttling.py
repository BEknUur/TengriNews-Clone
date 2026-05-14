# Python modules
from functools import wraps
from typing import Any, Callable

# Third-party modules
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class CustomAnonRateThrottle(AnonRateThrottle):
    """Throttle for unauthenticated requests."""
    scope = "anon"


class CustomUserRateThrottle(UserRateThrottle):
    """Throttle for authenticated requests."""
    scope = "user"


def throttle_scope(scope: str) -> Callable:
    """
    Mark a ViewSet action with a named throttle scope.

    Requires ActionThrottleMixin on the ViewSet. The scope must be listed
    in DEFAULT_THROTTLE_RATES. Example:

        @throttle_scope("article_create")
        @require_permissions(IsAuthenticated)
        def create(self, request):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)
        wrapper._throttle_scope = scope 
        return wrapper
    return decorator


class ActionThrottleMixin:
    """
    Reads _throttle_scope set by @throttle_scope() and applies it
    before DRF's throttle check. Must be the first parent in the MRO:

        class MyViewSet(ActionThrottleMixin, ViewSet, ...):
    """

    def get_throttles(self) -> list:
        action_name = getattr(self, "action", None)
        if action_name:
            fn = getattr(self, action_name, None)
            while fn is not None:
                scope = getattr(fn, "_throttle_scope", None)
                if scope:
                    self.throttle_scope = scope
                    break
                fn = getattr(fn, "__wrapped__", None)
        return super().get_throttles()
