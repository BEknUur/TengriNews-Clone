# Python modules
from typing import Any, Optional, Sequence
from urllib.parse import parse_qs, urlparse

# Third-party modules
from rest_framework.pagination import CursorPagination, LimitOffsetPagination, PageNumberPagination
from rest_framework.response import Response as DRFResponse
from rest_framework.utils.serializer_helpers import ReturnList


def _extract_cursor_token(link: Optional[str], param: str = "cursor") -> Optional[str]:
    """Extract a cursor token value from a pagination link URL."""
    if not link:
        return None
    vals = parse_qs(urlparse(link).query).get(param)
    return vals[-1] if vals else None


class AbstractCursorPaginator(CursorPagination):
    """Cursor paginator with a unified {pagination, data} response format."""

    DEFAULT_PAGE_SIZE = 20
    page_size_query_param = "page_size"
    cursor_query_param = "cursor"
    max_page_size = 200

    def __init__(
        self,
        page_size: int = DEFAULT_PAGE_SIZE,
        ordering: str | Sequence[str] = "-published_at",
        extra_data_return: Optional[dict[str, Any]] = None,
    ) -> None:
        self.page_size = min(page_size, self.max_page_size)
        self.ordering = ordering
        self.extra_data_return = extra_data_return or {}
        super().__init__()

    def get_paginated_response(self, data: ReturnList) -> DRFResponse:
        """Return {pagination: {...}, data: [...]} with cursor tokens."""
        next_link = self.get_next_link()
        prev_link = self.get_previous_link()
        return DRFResponse(
            {
                "pagination": {
                    "next": next_link,
                    "previous": prev_link,
                    "next_cursor": _extract_cursor_token(next_link, self.cursor_query_param),
                    "previous_cursor": _extract_cursor_token(prev_link, self.cursor_query_param),
                    "page_size": self.get_page_size(self.request),
                    "returned": len(data),
                    "max_page_size": self.max_page_size,
                    "ordering": self.ordering,
                },
                "data": data,
                **self.extra_data_return,
            }
        )


class AbstractPageNumberPaginator(PageNumberPagination):
    """Page-number paginator with a unified {pagination, data} response format."""

    page_size_query_param = "page_size"
    page_query_param = "page"
    DEFAULT_PAGE_SIZE = 10

    def __init__(self, page_size: int = DEFAULT_PAGE_SIZE) -> None:
        self.page_size = page_size
        super().__init__()

    def get_paginated_response(self, data: ReturnList) -> DRFResponse:
        """Return {pagination: {...}, data: [...]} with page links."""
        return DRFResponse(
            {
                "pagination": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                    "count": self.page.paginator.num_pages,
                },
                "data": data,
            }
        )


class AbstractLimitOffsetPaginator(LimitOffsetPagination):
    """Limit-offset paginator with a unified {pagination, data} response format."""

    limit: int = 10
    offset: int = 0
    limit_query_param = "limit"
    offset_query_param = "offset"
    default_limit = 10
    max_limit = 100

    def get_paginated_response(self, data: ReturnList) -> DRFResponse:
        """Return {pagination: {...}, data: [...]} with limit-offset links."""
        return DRFResponse(
            {
                "pagination": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "data": data,
            }
        )
