"""Request handling for the OMOPHub SDK."""

from __future__ import annotations

import contextlib
import json
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from ._exceptions import OMOPHubError, raise_for_status

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ._http import AsyncHTTPClient, HTTPClient
    from ._types import APIResponse, ErrorResponse

T = TypeVar("T")


class Request(Generic[T]):
    """Handles API request execution and response parsing."""

    def __init__(
        self,
        http_client: HTTPClient,
        base_url: str,
        api_key: str,
        vocab_version: str | None = None,
    ) -> None:
        self._http_client = http_client
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._vocab_version = vocab_version

    def _get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers."""
        headers = {"Authorization": f"Bearer {self._api_key}"}
        if self._vocab_version:
            headers["X-Vocab-Version"] = self._vocab_version
        return headers

    def _build_url(self, path: str) -> str:
        """Build full URL from path."""
        path = path.lstrip("/")
        return f"{self._base_url}/{path}"

    def _parse_response(
        self,
        content: bytes,
        status_code: int,
        headers: Mapping[str, str],
    ) -> T:
        """Parse API response and handle errors."""
        request_id = headers.get("X-Request-Id") or headers.get("x-request-id")

        try:
            data = json.loads(content) if content else {}
        except json.JSONDecodeError as exc:
            if status_code >= 400:
                raise_for_status(
                    status_code,
                    f"Request failed with status {status_code}",
                    request_id=request_id,
                )
            raise OMOPHubError(
                f"Invalid JSON response: {content[:200].decode(errors='replace')}"
            ) from exc

        # Handle error responses
        if status_code >= 400:
            error_response: ErrorResponse = data  # type: ignore[assignment]
            error = error_response.get("error", {})
            message = error.get("message", f"Request failed with status {status_code}")
            error_code = error.get("code")
            details = error.get("details")

            # Check for rate limit retry-after
            retry_after = None
            if status_code == 429:
                retry_after_header = headers.get("Retry-After") or headers.get(
                    "retry-after"
                )
                if retry_after_header:
                    with contextlib.suppress(ValueError):
                        retry_after = int(retry_after_header)

            raise_for_status(
                status_code,
                message,
                request_id=request_id,
                error_code=error_code,
                details=details,
                retry_after=retry_after,
            )

        # Return successful response data
        response: APIResponse = data  # type: ignore[assignment]
        return response.get("data", data)

    def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> T:
        """Make a GET request."""
        url = self._build_url(path)
        content, status_code, headers = self._http_client.request(
            "GET",
            url,
            headers=self._get_auth_headers(),
            params=params,
        )
        return self._parse_response(content, status_code, headers)

    def post(
        self,
        path: str,
        json_data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> T:
        """Make a POST request."""
        url = self._build_url(path)
        content, status_code, headers = self._http_client.request(
            "POST",
            url,
            headers=self._get_auth_headers(),
            params=params,
            json=json_data,
        )
        return self._parse_response(content, status_code, headers)


class AsyncRequest(Generic[T]):
    """Handles async API request execution and response parsing."""

    def __init__(
        self,
        http_client: AsyncHTTPClient,
        base_url: str,
        api_key: str,
        vocab_version: str | None = None,
    ) -> None:
        self._http_client = http_client
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._vocab_version = vocab_version

    def _get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers."""
        headers = {"Authorization": f"Bearer {self._api_key}"}
        if self._vocab_version:
            headers["X-Vocab-Version"] = self._vocab_version
        return headers

    def _build_url(self, path: str) -> str:
        """Build full URL from path."""
        path = path.lstrip("/")
        return f"{self._base_url}/{path}"

    def _parse_response(
        self,
        content: bytes,
        status_code: int,
        headers: Mapping[str, str],
    ) -> T:
        """Parse API response and handle errors."""
        request_id = headers.get("X-Request-Id") or headers.get("x-request-id")

        try:
            data = json.loads(content) if content else {}
        except json.JSONDecodeError as exc:
            if status_code >= 400:
                raise_for_status(
                    status_code,
                    f"Request failed with status {status_code}",
                    request_id=request_id,
                )
            raise OMOPHubError(
                f"Invalid JSON response: {content[:200].decode(errors='replace')}"
            ) from exc

        # Handle error responses
        if status_code >= 400:
            error_response: ErrorResponse = data  # type: ignore[assignment]
            error = error_response.get("error", {})
            message = error.get("message", f"Request failed with status {status_code}")
            error_code = error.get("code")
            details = error.get("details")

            # Check for rate limit retry-after
            retry_after = None
            if status_code == 429:
                retry_after_header = headers.get("Retry-After") or headers.get(
                    "retry-after"
                )
                if retry_after_header:
                    with contextlib.suppress(ValueError):
                        retry_after = int(retry_after_header)

            raise_for_status(
                status_code,
                message,
                request_id=request_id,
                error_code=error_code,
                details=details,
                retry_after=retry_after,
            )

        # Return successful response data
        response: APIResponse = data  # type: ignore[assignment]
        return response.get("data", data)

    async def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> T:
        """Make an async GET request."""
        url = self._build_url(path)
        content, status_code, headers = await self._http_client.request(
            "GET",
            url,
            headers=self._get_auth_headers(),
            params=params,
        )
        return self._parse_response(content, status_code, headers)

    async def post(
        self,
        path: str,
        json_data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> T:
        """Make an async POST request."""
        url = self._build_url(path)
        content, status_code, headers = await self._http_client.request(
            "POST",
            url,
            headers=self._get_auth_headers(),
            params=params,
            json=json_data,
        )
        return self._parse_response(content, status_code, headers)
