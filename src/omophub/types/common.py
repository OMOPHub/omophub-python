"""Common type definitions shared across the SDK."""

from __future__ import annotations

from typing import Any, TypedDict

from typing_extensions import NotRequired


class PaginationParams(TypedDict, total=False):
    """Common pagination parameters for list endpoints."""

    page: int
    page_size: int


class PaginationMeta(TypedDict):
    """Pagination metadata in API responses."""

    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class ResponseMeta(TypedDict, total=False):
    """Metadata included in API responses."""

    request_id: str
    timestamp: str
    vocab_release: str
    pagination: PaginationMeta


class APIResponse(TypedDict):
    """Standard API response structure."""

    success: bool
    data: Any
    meta: NotRequired[ResponseMeta]


class ErrorDetail(TypedDict):
    """Error detail in API error responses."""

    message: str
    code: NotRequired[str]
    details: NotRequired[dict[str, Any]]


class ErrorResponse(TypedDict):
    """Standard API error response structure."""

    success: bool
    error: ErrorDetail
