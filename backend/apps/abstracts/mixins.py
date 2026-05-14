"""Reusable DRF helper mixins for project views."""

# Python modules
from typing import Any, Optional, Type, TypeVar

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
    """Mixin to get DRF response."""

    def get_drf_response(
        self,
        request: DRFRequest,
        data: QuerySet | Manager,
        serializer_class: Type[Serializer],
        many: bool = False,
        paginator: Optional[BasePagination] = None,
        serializer_context: Optional[dict[str, Any]] = None,
        status_code: int = HTTP_200_OK,
    ) -> DRFResponse:
        """Get DRF response with optional pagination."""
        if not serializer_context:
            serializer_context = {"request": request}

        if paginator and many:
            objects: list = paginator.paginate_queryset(
                queryset=data, request=request, view=self
            )
            serializer: Serializer = serializer_class(
                objects, many=many, context=serializer_context
            )
            return paginator.get_paginated_response(serializer.data)

        serializer: Serializer = serializer_class(
            data, many=many, context=serializer_context
        )
        return DRFResponse(data=serializer.data, status=status_code)


class ModelInstanceMixin:
    """Mixin to get model instance."""

    def get_model_instance(
        self,
        model: Type[Model],
        **kwargs: dict[str, Any],
    ) -> Optional[Model]:
        """Get model instance or None."""
        try:
            return model.objects.get(**kwargs)
        except model.DoesNotExist:
            return None


class ViewSetWorkflowMixin:
    """Reusable ViewSet workflows for lookups and serializer execution."""

    def get_object_or_404_response(
        self,
        queryset: QuerySet[TModel] | Manager[TModel],
        *,
        response_data: Optional[dict[str, Any]] = None,
        status_code: int = HTTP_404_NOT_FOUND,
        **lookup: Any,
    ) -> tuple[Optional[TModel], Optional[DRFResponse]]:
        """Return queryset object or a DRF not-found response."""
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
        context: Optional[dict[str, Any]] = None,
    ) -> Serializer:
        """Build and validate serializer for create/update flows."""
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
        context: Optional[dict[str, Any]] = None,
    ) -> DRFResponse:
        """Serialize object(s) and wrap into DRF Response."""
        serializer = serializer_class(instance, many=many, context=context)
        return DRFResponse(data=serializer.data, status=status_code)
