# Python modules
from functools import wraps
from typing import Any, Callable, Type

# Third-party modules
from rest_framework.permissions import BasePermission
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.serializers import Serializer
from rest_framework.status import HTTP_400_BAD_REQUEST


def require_permissions(*permission_classes: Type[BasePermission]) -> Callable:
    """Validate permissions before executing the wrapped view method."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, request: DRFRequest, *args: Any, **kwargs: Any) -> DRFResponse:
            for permission_class in permission_classes:
                permission = permission_class()
                if not permission.has_permission(request, self):
                    self.permission_denied(
                        request,
                        message=getattr(permission, "message", None),
                        code=getattr(permission, "code", None),
                    )
            return func(self, request, *args, **kwargs)

        return wrapper

    return decorator


def validate_serializer_data(
    serializer_class: Type[Serializer],
    context: dict[str, Any] | None = None,
    many: bool = False,
) -> Callable:
    """Validate request payload and inject serializer + validated_data into kwargs."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, request: DRFRequest, *args: Any, **kwargs: Any) -> Any:
            local_context: dict[str, Any] = dict(context or {})
            local_context["request"] = request

            data = request.data if request.method in ("POST", "PUT", "PATCH") else request.query_params

            if "pk" in kwargs:
                local_context["pk"] = int(kwargs["pk"])
            if "object" in kwargs:
                local_context["object"] = kwargs["object"]

            serializer: Serializer = serializer_class(
                instance=local_context.get("object"),
                data=data,
                context=local_context,
                many=many,
                partial=request.method == "PATCH",
            )
            if serializer.is_valid():
                kwargs["validated_data"] = serializer.validated_data.copy()
                kwargs["serializer"] = serializer
                return func(self, request, *args, **kwargs)

            return DRFResponse(data=serializer.errors, status=HTTP_400_BAD_REQUEST)

        return wrapper

    return decorator
