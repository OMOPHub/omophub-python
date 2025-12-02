"""Exception hierarchy for the OMOPHub SDK."""

from __future__ import annotations

from typing import Any


class OMOPHubError(Exception):
    """Base exception for all OMOPHub SDK errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class APIError(OMOPHubError):
    """API returned an error response."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        request_id: str | None = None,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.status_code = status_code
        self.request_id = request_id
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)

    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code:
            parts.append(f"(status={self.status_code})")
        if self.request_id:
            parts.append(f"[request_id={self.request_id}]")
        return " ".join(parts)


class AuthenticationError(APIError):
    """Authentication failed (401) or forbidden (403)."""

    pass


class NotFoundError(APIError):
    """Resource not found (404)."""

    pass


class ValidationError(APIError):
    """Request validation failed (400)."""

    pass


class RateLimitError(APIError):
    """Rate limit exceeded (429)."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int = 429,
        retry_after: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, status_code=status_code, **kwargs)
        self.retry_after = retry_after


class ServerError(APIError):
    """Server-side error (5xx)."""

    pass


class ConnectionError(OMOPHubError):
    """Network connection error."""

    pass


class TimeoutError(OMOPHubError):
    """Request timeout error."""

    pass


# Error mapping by status code and error type
_ERROR_MAP: dict[int, type[APIError]] = {
    400: ValidationError,
    401: AuthenticationError,
    403: AuthenticationError,
    404: NotFoundError,
    429: RateLimitError,
}


def raise_for_status(
    status_code: int,
    message: str,
    *,
    request_id: str | None = None,
    error_code: str | None = None,
    details: dict[str, Any] | None = None,
    retry_after: int | None = None,
) -> None:
    """Raise the appropriate exception based on status code."""
    if status_code >= 500:
        raise ServerError(
            message,
            status_code=status_code,
            request_id=request_id,
            error_code=error_code,
            details=details,
        )

    error_class = _ERROR_MAP.get(status_code, APIError)

    if error_class is RateLimitError:
        raise RateLimitError(
            message,
            status_code=status_code,
            request_id=request_id,
            error_code=error_code,
            details=details,
            retry_after=retry_after,
        )

    raise error_class(
        message,
        status_code=status_code,
        request_id=request_id,
        error_code=error_code,
        details=details,
    )
