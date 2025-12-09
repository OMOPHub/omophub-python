"""HTTP client abstraction for the OMOPHub SDK."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

import httpx

from ._config import DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT
from ._exceptions import ConnectionError, TimeoutError
from ._version import get_version

if TYPE_CHECKING:
    from collections.abc import Mapping

# Check if HTTP/2 support is available
try:
    import h2  # type: ignore[import-not-found]  # noqa: F401

    HTTP2_AVAILABLE = True
except ImportError:
    HTTP2_AVAILABLE = False


class HTTPClient(ABC):
    """Abstract base class for HTTP clients."""

    @abstractmethod
    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> tuple[bytes, int, Mapping[str, str]]:
        """Make an HTTP request.

        Returns:
            Tuple of (response body bytes, status code, response headers)
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the HTTP client."""
        pass


class AsyncHTTPClient(ABC):
    """Abstract base class for async HTTP clients."""

    @abstractmethod
    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> tuple[bytes, int, Mapping[str, str]]:
        """Make an async HTTP request.

        Returns:
            Tuple of (response body bytes, status code, response headers)
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the async HTTP client."""
        pass


class SyncHTTPClient(HTTPClient):
    """Synchronous HTTP client using httpx."""

    def __init__(
        self,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self._timeout = timeout
        self._max_retries = max_retries
        self._client: httpx.Client | None = None

    def _get_client(self) -> httpx.Client:
        """Get or create the httpx client."""
        if self._client is None:
            self._client = httpx.Client(
                timeout=self._timeout,
                http2=HTTP2_AVAILABLE,
            )
        return self._client

    def _get_default_headers(self) -> dict[str, str]:
        """Get default headers for all requests."""
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": f"OMOPHub-SDK-Python/{get_version()}",
        }

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> tuple[bytes, int, Mapping[str, str]]:
        """Make an HTTP request with retry logic."""
        client = self._get_client()

        # Merge headers
        request_headers = self._get_default_headers()
        if headers:
            request_headers.update(headers)

        # Filter None values from params
        filtered_params = {k: v for k, v in (params or {}).items() if v is not None}

        last_exception: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                response = client.request(
                    method,
                    url,
                    headers=request_headers,
                    params=filtered_params if filtered_params else None,
                    json=json,
                )
                return response.content, response.status_code, response.headers

            except httpx.ConnectError as e:
                last_exception = ConnectionError(f"Connection error: {e}")
            except httpx.TimeoutException as e:
                last_exception = TimeoutError(f"Request timed out: {e}")
            except httpx.HTTPError as e:
                last_exception = ConnectionError(f"HTTP error: {e}")

            # Exponential backoff before retry
            if attempt < self._max_retries:
                time.sleep(2**attempt * 0.1)

        raise last_exception or ConnectionError("Request failed after retries")

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None


class AsyncHTTPClientImpl(AsyncHTTPClient):
    """Asynchronous HTTP client implementation using httpx."""

    def __init__(
        self,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self._timeout = timeout
        self._max_retries = max_retries
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the async httpx client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self._timeout,
                http2=HTTP2_AVAILABLE,
            )
        return self._client

    def _get_default_headers(self) -> dict[str, str]:
        """Get default headers for all requests."""
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": f"OMOPHub-SDK-Python/{get_version()}",
        }

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> tuple[bytes, int, Mapping[str, str]]:
        """Make an async HTTP request with retry logic."""
        import asyncio

        client = await self._get_client()

        # Merge headers
        request_headers = self._get_default_headers()
        if headers:
            request_headers.update(headers)

        # Filter None values from params
        filtered_params = {k: v for k, v in (params or {}).items() if v is not None}

        last_exception: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                response = await client.request(
                    method,
                    url,
                    headers=request_headers,
                    params=filtered_params if filtered_params else None,
                    json=json,
                )
                return response.content, response.status_code, response.headers

            except httpx.ConnectError as e:
                last_exception = ConnectionError(f"Connection error: {e}")
            except httpx.TimeoutException as e:
                last_exception = TimeoutError(f"Request timed out: {e}")
            except httpx.HTTPError as e:
                last_exception = ConnectionError(f"HTTP error: {e}")

            # Exponential backoff before retry
            if attempt < self._max_retries:
                await asyncio.sleep(2**attempt * 0.1)

        raise last_exception or ConnectionError("Request failed after retries")

    async def close(self) -> None:
        """Close the async HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
