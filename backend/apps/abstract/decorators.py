"""Reusable decorators for DRF views."""

# Python modules
from functools import wraps
from typing import Any, Callable, Optional, Type, TypeVar

# Django modules
from django.db.models import Manager, Model, QuerySet

# Django REST Framework
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.serializers import Serializer
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND


T = TypeVar('T', bound=Model)


def validate_serializer_data(
    serializer_class: Type[Serializer],
    context: Optional[dict[str, Any]] = None,
    many: bool = False,
) -> Callable:
    # Purpose: validate request input once and pass validated data to view method.
    def decorator(
        func: Callable[[DRFRequest, tuple[Any, ...], dict[Any, Any]], DRFResponse],
    ) -> Callable:
        @wraps(func)
        def wrapper(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[Any, Any],
        ):
            local_context: dict[str, Any] = dict(context or {})
            local_context['request'] = request

            # Purpose: choose body for mutating methods and query params for read methods.
            if request.method in ('POST', 'PUT', 'PATCH'):
                data = request.data
            else:
                data = request.query_params

            if 'pk' in kwargs:
                local_context['pk'] = int(kwargs['pk'])

            if 'object' in kwargs:
                local_context['object'] = kwargs['object']

            serializer: Serializer = serializer_class(
                instance=local_context.get('object'),
                data=data,
                context=local_context,
                many=many,
                partial=request.method == 'PATCH',
            )
            if serializer.is_valid():
                kwargs['validated_data'] = serializer.validated_data.copy()
                kwargs['serializer'] = serializer
                return func(self, request, *args, **kwargs)

            return DRFResponse(
                data=serializer.errors,
                status=HTTP_400_BAD_REQUEST,
            )

        return wrapper

    return decorator


def find_queryset_object_by_query_pk(
    queryset: QuerySet[T] | Manager[T],
    entity_name: str,
) -> Callable:
    # Purpose: fetch object by URL `pk` once and provide consistent 400/404 responses.
    def decorator(
        func: Callable[[DRFRequest, tuple[Any, ...], dict[Any, Any]], DRFResponse],
    ) -> Callable:
        @wraps(func)
        def wrapper(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[Any, Any],
        ) -> DRFResponse:
            pk: Optional[str] = kwargs.get('pk', None)
            assert pk is not None, 'Primary key is not provided'

            if not pk.isdigit():
                return DRFResponse(
                    data={
                        'id': [
                            f'{entity_name} ID must be a number.',
                        ]
                    },
                    status=HTTP_400_BAD_REQUEST,
                )
            try:
                kwargs['object'] = queryset.get(pk=pk)
                return func(self, request, *args, **kwargs)
            except queryset.model.DoesNotExist:
                return DRFResponse(
                    data={
                        'id': [
                            f"{entity_name} with ID {pk} hasn't been found.",
                        ]
                    },
                    status=HTTP_404_NOT_FOUND,
                )
            except queryset.model.MultipleObjectsReturned:
                return DRFResponse(
                    data={
                        'id': [
                            f'Multiple {entity_name} objects returned for ID {pk}.',
                        ],
                    },
                    status=HTTP_400_BAD_REQUEST,
                )

        return wrapper

    return decorator
