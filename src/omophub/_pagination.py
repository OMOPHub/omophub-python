"""Pagination utilities for the OMOPHub SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar
from urllib.parse import urlencode

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Callable, Iterator

    from ._types import PaginationMeta

T = TypeVar("T")

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 1000


class PaginationHelper:
    """Helper class for building paginated requests."""

    @staticmethod
    def build_query_string(
        params: dict[str, Any] | None = None,
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> str:
        """Build a query string with pagination parameters.

        Args:
            params: Additional query parameters
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            URL-encoded query string
        """
        query_params: dict[str, Any] = {
            "page": page,
            "page_size": min(page_size, MAX_PAGE_SIZE),
        }

        if params:
            # Filter None values and add to query params
            for key, value in params.items():
                if value is not None:
                    if isinstance(value, list):
                        query_params[key] = ",".join(str(v) for v in value)
                    else:
                        query_params[key] = value

        return urlencode(query_params)

    @staticmethod
    def build_paginated_path(
        base_path: str,
        params: dict[str, Any] | None = None,
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> str:
        """Build a full path with query parameters.

        Args:
            base_path: The base API path
            params: Additional query parameters
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            Full path with query string
        """
        query_string = PaginationHelper.build_query_string(params, page, page_size)
        separator = "&" if "?" in base_path else "?"
        return f"{base_path}{separator}{query_string}"

    @staticmethod
    def has_more_pages(meta: PaginationMeta) -> bool:
        """Check if there are more pages available."""
        return meta.get("has_next", False)


def paginate_sync(
    fetch_page: Callable[[int, int], tuple[list[T], PaginationMeta | None]],
    page_size: int = DEFAULT_PAGE_SIZE,
) -> Iterator[T]:
    """Create a synchronous iterator that auto-paginates through results.

    Args:
        fetch_page: Callable that takes (page, page_size) and returns (items, pagination_meta)
        page_size: Number of items per page

    Yields:
        Individual items from all pages
    """
    page = 1

    while True:
        items, meta = fetch_page(page, page_size)

        yield from items

        if meta is None or not PaginationHelper.has_more_pages(meta):
            break

        page += 1


async def paginate_async(
    fetch_page: Callable[[int, int], tuple[list[T], PaginationMeta | None]],
    page_size: int = DEFAULT_PAGE_SIZE,
) -> AsyncIterator[T]:
    """Create an async iterator that auto-paginates through results.

    Args:
        fetch_page: Async callable that takes (page, page_size) and returns (items, pagination_meta)
        page_size: Number of items per page

    Yields:
        Individual items from all pages
    """
    page = 1

    while True:
        # Note: fetch_page should be an async function
        result = fetch_page(page, page_size)
        if hasattr(result, "__await__"):
            items, meta = await result  # type: ignore
        else:
            items, meta = result

        for item in items:
            yield item

        if meta is None or not PaginationHelper.has_more_pages(meta):
            break

        page += 1
