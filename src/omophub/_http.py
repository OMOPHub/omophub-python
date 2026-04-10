"""HTTP client abstraction for the OMOPHub SDK."""

from __future__ import annotations

import random
import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

import httpx

from ._config import DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT
from ._exceptions import ConnectionError, TimeoutError
from ._version import get_version

# Retry constants (OpenAI-style exponential backoff with jitter)
INITIAL_RETRY_DELAY = 0.5  # seconds
MAX_RETRY_DELAY = 8.0  # seconds
MAX_RETRY_AFTER = 60  # max seconds to respect from Retry-After header
RETRYABLE_STATUS_CODES = (429, 502, 503, 504)

if TYPE_CHECKING:
    from collections.abc import Mapping

# Check if HTTP/2 support is available
try:
    import h2  # type: ignore[import-not-found]  # noqa: F401

    HTTP2_AVAILABLE = True
except ImportError:
    HTTP2_AVAILABLE = False


def _calculate_retry_delay(
    attempt: int,
    max_retries: int,
    response_headers: Mapping[str, str] | None = None,
) -> float:
    """Calculate retry delay with Retry-After support and exponential backoff + jitter.

    Follows the OpenAI pattern:
    1. If Retry-After header present and <= 60s, use it
    2. Otherwise, exponential backoff (0.5s * 2^attempt) with 25% jitter, capped at 8s
    """
    # Check Retry-After header first
    if response_headers:
        retry_after = response_headers.get("retry-after") or response_headers.get(
            "Retry-After"
        )
        if retry_after:
            try:
                retry_after_seconds = float(retry_after)
                if 0 < retry_after_seconds <= MAX_RETRY_AFTER:
                    return retry_after_seconds
            except ValueError:
                pass

    # Exponential backoff with jitter
    retries_done = min(max_retries - (max_retries - attempt), 1000)
    sleep_seconds = min(INITIAL_RETRY_DELAY * (2.0**retries_done), MAX_RETRY_DELAY)
    jitter = 1 - 0.25 * random.random()
    return sleep_seconds * jitter


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
                # Retry on rate limits (429) and server errors (502, 503, 504)
                if (
                    response.status_code in RETRYABLE_STATUS_CODES
                    and attempt < self._max_retries
                ):
                    delay = _calculate_retry_delay(
                        attempt, self._max_retries, response.headers
                    )
                    time.sleep(delay)
                    continue
                return response.content, response.status_code, response.headers

            except httpx.ConnectError as e:
                last_exception = ConnectionError(f"Connection error: {e}")
            except httpx.TimeoutException as e:
                last_exception = TimeoutError(f"Request timed out: {e}")
            except httpx.HTTPError as e:
                last_exception = ConnectionError(f"HTTP error: {e}")

            # Exponential backoff before retry
            if attempt < self._max_retries:
                delay = _calculate_retry_delay(attempt, self._max_retries)
                time.sleep(delay)

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
                # Retry on rate limits (429) and server errors (502, 503, 504)
                if (
                    response.status_code in RETRYABLE_STATUS_CODES
                    and attempt < self._max_retries
                ):
                    delay = _calculate_retry_delay(
                        attempt, self._max_retries, response.headers
                    )
                    await asyncio.sleep(delay)
                    continue
                return response.content, response.status_code, response.headers

            except httpx.ConnectError as e:
                last_exception = ConnectionError(f"Connection error: {e}")
            except httpx.TimeoutException as e:
                last_exception = TimeoutError(f"Request timed out: {e}")
            except httpx.HTTPError as e:
                last_exception = ConnectionError(f"HTTP error: {e}")

            # Exponential backoff before retry
            if attempt < self._max_retries:
                delay = _calculate_retry_delay(attempt, self._max_retries)
                await asyncio.sleep(delay)

        raise last_exception or ConnectionError("Request failed after retries")

    async def close(self) -> None:
        """Close the async HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
