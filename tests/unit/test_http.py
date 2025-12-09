"""Tests for HTTP client abstraction."""

from __future__ import annotations

from unittest.mock import patch

import httpx
import pytest
import respx
from httpx import Response

from omophub._exceptions import ConnectionError, TimeoutError
from omophub._http import (
    HTTP2_AVAILABLE,
    AsyncHTTPClientImpl,
    SyncHTTPClient,
)


class TestSyncHTTPClient:
    """Tests for SyncHTTPClient."""

    def test_request_success(self) -> None:
        """Test successful HTTP request."""
        client = SyncHTTPClient(timeout=30.0, max_retries=0)

        with respx.mock:
            respx.get("https://api.example.com/test").mock(
                return_value=Response(200, json={"success": True})
            )

            content, status_code, headers = client.request(
                "GET", "https://api.example.com/test"
            )

            assert status_code == 200
            assert b"success" in content

        client.close()

    def test_request_with_headers(self) -> None:
        """Test request with custom headers."""
        client = SyncHTTPClient()

        with respx.mock:
            route = respx.get("https://api.example.com/test").mock(
                return_value=Response(200, json={})
            )

            client.request(
                "GET",
                "https://api.example.com/test",
                headers={"Authorization": "Bearer token123"},
            )

            assert "Authorization" in route.calls[0].request.headers
            assert route.calls[0].request.headers["Authorization"] == "Bearer token123"

        client.close()

    def test_request_with_params(self) -> None:
        """Test request with query parameters."""
        client = SyncHTTPClient()

        with respx.mock:
            route = respx.get("https://api.example.com/test").mock(
                return_value=Response(200, json={})
            )

            client.request(
                "GET",
                "https://api.example.com/test",
                params={"query": "diabetes", "page": 1},
            )

            assert "query=diabetes" in str(route.calls[0].request.url)
            assert "page=1" in str(route.calls[0].request.url)

        client.close()

    def test_request_filters_none_params(self) -> None:
        """Test that None values are filtered from params."""
        client = SyncHTTPClient()

        with respx.mock:
            route = respx.get("https://api.example.com/test").mock(
                return_value=Response(200, json={})
            )

            client.request(
                "GET",
                "https://api.example.com/test",
                params={"query": "diabetes", "domain": None},
            )

            url_str = str(route.calls[0].request.url)
            assert "query=diabetes" in url_str
            assert "domain" not in url_str

        client.close()

    def test_request_with_json_body(self) -> None:
        """Test request with JSON body."""
        client = SyncHTTPClient()

        with respx.mock:
            route = respx.post("https://api.example.com/test").mock(
                return_value=Response(200, json={})
            )

            client.request(
                "POST",
                "https://api.example.com/test",
                json={"concept_ids": [1, 2, 3]},
            )

            # httpx serializes without spaces
            assert route.calls[0].request.content == b'{"concept_ids":[1,2,3]}'

        client.close()

    def test_connection_error(self) -> None:
        """Test handling of connection errors."""
        client = SyncHTTPClient(max_retries=0)

        with respx.mock:
            respx.get("https://api.example.com/test").mock(
                side_effect=httpx.ConnectError("Connection refused")
            )

            with pytest.raises(ConnectionError) as exc_info:
                client.request("GET", "https://api.example.com/test")

            assert "Connection error" in str(exc_info.value)

        client.close()

    def test_timeout_error(self) -> None:
        """Test handling of timeout errors."""
        client = SyncHTTPClient(max_retries=0)

        with respx.mock:
            respx.get("https://api.example.com/test").mock(
                side_effect=httpx.TimeoutException("Request timed out")
            )

            with pytest.raises(TimeoutError) as exc_info:
                client.request("GET", "https://api.example.com/test")

            assert "timed out" in str(exc_info.value)

        client.close()

    def test_retry_on_connection_error(self) -> None:
        """Test retry logic on connection errors."""
        client = SyncHTTPClient(max_retries=2)
        call_count = 0

        def side_effect(request: httpx.Request) -> Response:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.ConnectError("Connection refused")
            return Response(200, json={"success": True})

        with respx.mock:
            respx.get("https://api.example.com/test").mock(side_effect=side_effect)

            with patch("time.sleep"):  # Skip actual sleep
                content, status_code, _ = client.request(
                    "GET", "https://api.example.com/test"
                )

            assert status_code == 200
            assert call_count == 3

        client.close()

    def test_max_retries_exceeded(self) -> None:
        """Test that max retries are respected."""
        client = SyncHTTPClient(max_retries=2)

        with respx.mock:
            respx.get("https://api.example.com/test").mock(
                side_effect=httpx.ConnectError("Connection refused")
            )

            with patch("time.sleep"):  # Skip actual sleep
                with pytest.raises(ConnectionError):
                    client.request("GET", "https://api.example.com/test")

        client.close()

    def test_default_headers(self) -> None:
        """Test that default headers are set correctly."""
        client = SyncHTTPClient()
        headers = client._get_default_headers()

        assert "Accept" in headers
        assert headers["Accept"] == "application/json"
        assert "Content-Type" in headers
        assert headers["Content-Type"] == "application/json"
        assert "User-Agent" in headers
        assert "OMOPHub-SDK-Python" in headers["User-Agent"]

        client.close()

    def test_close_idempotent(self) -> None:
        """Test that close can be called multiple times safely."""
        client = SyncHTTPClient()
        client.close()
        client.close()  # Should not raise

    def test_client_reuse(self) -> None:
        """Test that client is reused for multiple requests."""
        client = SyncHTTPClient()

        with respx.mock:
            respx.get("https://api.example.com/test").mock(
                return_value=Response(200, json={})
            )

            client.request("GET", "https://api.example.com/test")
            first_client = client._client

            client.request("GET", "https://api.example.com/test")
            second_client = client._client

            assert first_client is second_client

        client.close()


class TestAsyncHTTPClient:
    """Tests for AsyncHTTPClientImpl."""

    @pytest.mark.asyncio
    async def test_request_success(self) -> None:
        """Test successful async HTTP request."""
        client = AsyncHTTPClientImpl(timeout=30.0, max_retries=0)

        with respx.mock:
            respx.get("https://api.example.com/test").mock(
                return_value=Response(200, json={"success": True})
            )

            content, status_code, headers = await client.request(
                "GET", "https://api.example.com/test"
            )

            assert status_code == 200
            assert b"success" in content

        await client.close()

    @pytest.mark.asyncio
    async def test_request_with_headers(self) -> None:
        """Test async request with custom headers."""
        client = AsyncHTTPClientImpl()

        with respx.mock:
            route = respx.get("https://api.example.com/test").mock(
                return_value=Response(200, json={})
            )

            await client.request(
                "GET",
                "https://api.example.com/test",
                headers={"Authorization": "Bearer token123"},
            )

            assert "Authorization" in route.calls[0].request.headers
            assert route.calls[0].request.headers["Authorization"] == "Bearer token123"

        await client.close()

    @pytest.mark.asyncio
    async def test_connection_error(self) -> None:
        """Test async handling of connection errors."""
        client = AsyncHTTPClientImpl(max_retries=0)

        with respx.mock:
            respx.get("https://api.example.com/test").mock(
                side_effect=httpx.ConnectError("Connection refused")
            )

            with pytest.raises(ConnectionError) as exc_info:
                await client.request("GET", "https://api.example.com/test")

            assert "Connection error" in str(exc_info.value)

        await client.close()

    @pytest.mark.asyncio
    async def test_timeout_error(self) -> None:
        """Test async handling of timeout errors."""
        client = AsyncHTTPClientImpl(max_retries=0)

        with respx.mock:
            respx.get("https://api.example.com/test").mock(
                side_effect=httpx.TimeoutException("Request timed out")
            )

            with pytest.raises(TimeoutError) as exc_info:
                await client.request("GET", "https://api.example.com/test")

            assert "timed out" in str(exc_info.value)

        await client.close()

    @pytest.mark.asyncio
    async def test_retry_on_error(self) -> None:
        """Test async retry logic on errors."""
        client = AsyncHTTPClientImpl(max_retries=2)
        call_count = 0

        def side_effect(request: httpx.Request) -> Response:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.ConnectError("Connection refused")
            return Response(200, json={"success": True})

        with respx.mock:
            respx.get("https://api.example.com/test").mock(side_effect=side_effect)

            with patch("asyncio.sleep"):  # Skip actual sleep
                content, status_code, _ = await client.request(
                    "GET", "https://api.example.com/test"
                )

            assert status_code == 200
            assert call_count == 3

        await client.close()

    @pytest.mark.asyncio
    async def test_close_idempotent(self) -> None:
        """Test that async close can be called multiple times safely."""
        client = AsyncHTTPClientImpl()
        await client.close()
        await client.close()  # Should not raise

    @pytest.mark.asyncio
    async def test_default_headers(self) -> None:
        """Test that async client has correct default headers."""
        client = AsyncHTTPClientImpl()
        headers = client._get_default_headers()

        assert "Accept" in headers
        assert headers["Accept"] == "application/json"
        assert "User-Agent" in headers
        assert "OMOPHub-SDK-Python" in headers["User-Agent"]

        await client.close()


class TestHTTP2Detection:
    """Tests for HTTP/2 support detection."""

    def test_http2_available_is_bool(self) -> None:
        """Test that HTTP2_AVAILABLE is a boolean."""
        assert isinstance(HTTP2_AVAILABLE, bool)

    def test_client_respects_http2_availability(self) -> None:
        """Test that client uses HTTP/2 based on availability."""
        # This just verifies the code path works; actual HTTP/2 depends on h2 package
        client = SyncHTTPClient()

        with respx.mock:
            respx.get("https://api.example.com/test").mock(
                return_value=Response(200, json={})
            )
            client.request("GET", "https://api.example.com/test")

        client.close()
