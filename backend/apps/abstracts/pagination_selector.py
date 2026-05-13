from typing import Optional, Any
from django.conf import settings
from rest_framework.pagination import BasePagination
from rest_framework.request import Request as DRFRequest

from apps.abstracts.paginators import (
    AbstractCursorPaginator,
    AbstractPageNumberPaginator,
    AbstractLimitOffsetPaginator,
)

PAGINATION_MAP = {
    "cursor": lambda: AbstractCursorPaginator(
        page_size=getattr(settings, "DEFAULT_PAGE_SIZE", 20)
    ),
    "page": lambda: AbstractPageNumberPaginator(
        page_size=getattr(settings, "DEFAULT_PAGE_SIZE", 20)
    ),
    "limit": lambda: AbstractLimitOffsetPaginator(),
}


def get_paginator(
    request: DRFRequest,
    view: Any,
    default: str = "cursor",
) -> Optional[BasePagination]:
    pagination_type = request.query_params.get("pagination", default)
    factory = PAGINATION_MAP.get(pagination_type)
    return factory() if factory else None
