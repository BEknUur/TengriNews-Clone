# Python modules
from typing import Any, Type, TypeVar

# Django modules
from django.db.models import Manager, Model, QuerySet

# Third-party modules
from rest_framework.pagination import BasePagination
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.serializers import Serializer
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND

TModel = TypeVar("TModel", bound=Model)


class DRFResponseMixin:
    """Mixin providing a paginated DRF response helper."""

    def get_drf_response(
        self,
        request: DRFRequest,
        data: QuerySet | Manager,
        serializer_class: Type[Serializer],
        many: bool = False,
        paginator: BasePagination | None = None,
        serializer_context: dict[str, Any] | None = None,
        status_code: int = HTTP_200_OK,
    ) -> DRFResponse:
        """Serialize data and return a DRF response, with optional pagination."""
        if not serializer_context:
            serializer_context = {"request": request}

        if paginator and many:
            objects: list = paginator.paginate_queryset(
                queryset=data, request=request, view=self
            )
            serializer = serializer_class(objects, many=many, context=serializer_context)
            return paginator.get_paginated_response(serializer.data)

        serializer = serializer_class(data, many=many, context=serializer_context)
        return DRFResponse(data=serializer.data, status=status_code)


class ViewSetWorkflowMixin:
    """Reusable ViewSet workflows for lookups and serializer execution."""

    def get_object_or_404_response(
        self,
        queryset: QuerySet[TModel] | Manager[TModel],
        *,
        response_data: dict[str, Any] | None = None,
        status_code: int = HTTP_404_NOT_FOUND,
        **lookup: Any,
    ) -> tuple[TModel | None, DRFResponse | None]:
        """Return (object, None) or (None, 404 response)."""
        if response_data is None:
            response_data = {"detail": "Not found."}
        try:
            return queryset.get(**lookup), None
        except queryset.model.DoesNotExist:
            return None, DRFResponse(response_data, status=status_code)

    def validate_request_serializer(
        self,
        serializer_class: Type[Serializer],
        *,
        request: DRFRequest,
        instance: Any = None,
        data: Any = None,
        partial: bool = False,
        context: dict[str, Any] | None = None,
    ) -> Serializer:
        """Build, validate, and return a serializer for create/update flows."""
        serializer = serializer_class(
            instance=instance,
            data=request.data if data is None else data,
            partial=partial,
            context=context,
        )
        serializer.is_valid(raise_exception=True)
        return serializer

    def serialize_to_response(
        self,
        *,
        serializer_class: Type[Serializer],
        instance: Any,
        status_code: int = HTTP_200_OK,
        many: bool = False,
        context: dict[str, Any] | None = None,
    ) -> DRFResponse:
        """Serialize instance(s) and return a DRF response."""
        serializer = serializer_class(instance, many=many, context=context)
        return DRFResponse(data=serializer.data, status=status_code)
