"""Tests for request handling."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from omophub._exceptions import (
    AuthenticationError,
    NotFoundError,
    OMOPHubError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from omophub._http import AsyncHTTPClientImpl, SyncHTTPClient
from omophub._request import AsyncRequest, Request


class TestSyncRequest:
    """Tests for synchronous Request class."""

    @pytest.fixture
    def http_client(self) -> SyncHTTPClient:
        """Create HTTP client for tests."""
        return SyncHTTPClient(max_retries=0)

    @pytest.fixture
    def request_handler(self, http_client: SyncHTTPClient) -> Request:
        """Create request handler for tests."""
        return Request(
            http_client=http_client,
            base_url="https://api.example.com/v1",
            api_key="test_api_key",
        )

    def test_get_request(self, request_handler: Request) -> None:
        """Test GET request."""
        with respx.mock:
            respx.get("https://api.example.com/v1/concepts/123").mock(
                return_value=Response(
                    200,
                    json={
                        "success": True,
                        "data": {"concept_id": 123, "concept_name": "Test"},
                    },
                )
            )

            result = request_handler.get("/concepts/123")
            assert result["concept_id"] == 123

    def test_get_request_with_params(self, request_handler: Request) -> None:
        """Test GET request with query parameters."""
        with respx.mock:
            route = respx.get("https://api.example.com/v1/search").mock(
                return_value=Response(200, json={"success": True, "data": []})
            )

            request_handler.get("/search", params={"query": "diabetes", "page": 1})

            url_str = str(route.calls[0].request.url)
            assert "query=diabetes" in url_str
            assert "page=1" in url_str

    def test_post_request(self, request_handler: Request) -> None:
        """Test POST request."""
        with respx.mock:
            route = respx.post("https://api.example.com/v1/concepts/batch").mock(
                return_value=Response(
                    200,
                    json={"success": True, "data": {"concepts": []}},
                )
            )

            result = request_handler.post(
                "/concepts/batch", json_data={"concept_ids": [1, 2, 3]}
            )

            # httpx serializes JSON without spaces
            assert route.calls[0].request.content == b'{"concept_ids":[1,2,3]}'
            assert "concepts" in result

    def test_auth_header_included(self, request_handler: Request) -> None:
        """Test that Authorization header is included."""
        with respx.mock:
            route = respx.get("https://api.example.com/v1/test").mock(
                return_value=Response(200, json={"success": True, "data": {}})
            )

            request_handler.get("/test")

            assert "Authorization" in route.calls[0].request.headers
            assert (
                route.calls[0].request.headers["Authorization"] == "Bearer test_api_key"
            )

    def test_vocab_version_header(self) -> None:
        """Test that vocab version header is included when specified."""
        http_client = SyncHTTPClient(max_retries=0)
        request_handler = Request(
            http_client=http_client,
            base_url="https://api.example.com/v1",
            api_key="test_api_key",
            vocab_version="2024.4",
        )

        with respx.mock:
            route = respx.get("https://api.example.com/v1/test").mock(
                return_value=Response(200, json={"success": True, "data": {}})
            )

            request_handler.get("/test")

            assert "X-Vocab-Version" in route.calls[0].request.headers
            assert route.calls[0].request.headers["X-Vocab-Version"] == "2024.4"

    def test_request_id_extraction(self, request_handler: Request) -> None:
        """Test request ID is extracted from headers on error."""
        with respx.mock:
            respx.get("https://api.example.com/v1/test").mock(
                return_value=Response(
                    404,
                    json={
                        "success": False,
                        "error": {"message": "Not found", "code": "not_found"},
                    },
                    headers={"X-Request-Id": "req_abc123"},
                )
            )

            with pytest.raises(NotFoundError) as exc_info:
                request_handler.get("/test")

            assert exc_info.value.request_id == "req_abc123"

    def test_error_parsing_400(self, request_handler: Request) -> None:
        """Test 400 error parsing."""
        with respx.mock:
            respx.get("https://api.example.com/v1/test").mock(
                return_value=Response(
                    400,
                    json={
                        "success": False,
                        "error": {
                            "message": "Invalid request",
                            "code": "validation_error",
                            "details": {"field": "query"},
                        },
                    },
                )
            )

            with pytest.raises(ValidationError) as exc_info:
                request_handler.get("/test")

            assert exc_info.value.status_code == 400
            assert "Invalid request" in exc_info.value.message

    def test_error_parsing_401(self, request_handler: Request) -> None:
        """Test 401 error parsing."""
        with respx.mock:
            respx.get("https://api.example.com/v1/test").mock(
                return_value=Response(
                    401,
                    json={
                        "success": False,
                        "error": {"message": "Unauthorized", "code": "auth_error"},
                    },
                )
            )

            with pytest.raises(AuthenticationError) as exc_info:
                request_handler.get("/test")

            assert exc_info.value.status_code == 401

    def test_error_parsing_429_with_retry_after(self, request_handler: Request) -> None:
        """Test 429 error parsing with Retry-After header."""
        with respx.mock:
            respx.get("https://api.example.com/v1/test").mock(
                return_value=Response(
                    429,
                    json={
                        "success": False,
                        "error": {"message": "Rate limited"},
                    },
                    headers={"Retry-After": "60"},
                )
            )

            with pytest.raises(RateLimitError) as exc_info:
                request_handler.get("/test")

            assert exc_info.value.status_code == 429
            assert exc_info.value.retry_after == 60

    def test_error_parsing_500(self, request_handler: Request) -> None:
        """Test 500 error parsing."""
        with respx.mock:
            respx.get("https://api.example.com/v1/test").mock(
                return_value=Response(
                    500,
                    json={
                        "success": False,
                        "error": {"message": "Internal server error"},
                    },
                )
            )

            with pytest.raises(ServerError) as exc_info:
                request_handler.get("/test")

            assert exc_info.value.status_code == 500

    def test_json_decode_error(self, request_handler: Request) -> None:
        """Test handling of invalid JSON response."""
        with respx.mock:
            respx.get("https://api.example.com/v1/test").mock(
                return_value=Response(200, content=b"not json")
            )

            with pytest.raises(OMOPHubError) as exc_info:
                request_handler.get("/test")

            assert "Invalid JSON" in str(exc_info.value)

    def test_json_decode_error_on_error_status(self, request_handler: Request) -> None:
        """Test handling of invalid JSON on error status code."""
        with respx.mock:
            respx.get("https://api.example.com/v1/test").mock(
                return_value=Response(500, content=b"Internal Server Error")
            )

            with pytest.raises(ServerError):
                request_handler.get("/test")

    def test_response_without_data_wrapper(self, request_handler: Request) -> None:
        """Test response that doesn't have data wrapper returns raw data."""
        with respx.mock:
            respx.get("https://api.example.com/v1/test").mock(
                return_value=Response(200, json={"concept_id": 123})
            )

            result = request_handler.get("/test")
            assert result["concept_id"] == 123

    def test_url_building(self) -> None:
        """Test URL building with various path formats."""
        http_client = SyncHTTPClient(max_retries=0)
        request = Request(
            http_client=http_client,
            base_url="https://api.example.com/v1/",  # Trailing slash
            api_key="test",
        )

        # Test with leading slash
        assert request._build_url("/concepts") == "https://api.example.com/v1/concepts"
        # Test without leading slash
        assert request._build_url("concepts") == "https://api.example.com/v1/concepts"

    def test_get_raw_request(self, request_handler: Request) -> None:
        """Test get_raw returns full response with data and meta."""
        with respx.mock:
            respx.get("https://api.example.com/v1/search").mock(
                return_value=Response(
                    200,
                    json={
                        "success": True,
                        "data": {"concepts": [{"concept_id": 1}]},
                        "meta": {"pagination": {"page": 1, "total_pages": 5}},
                    },
                )
            )
            result = request_handler.get_raw("/search")
            assert "data" in result
            assert "meta" in result
            assert result["meta"]["pagination"]["page"] == 1
            assert result["meta"]["pagination"]["total_pages"] == 5

    def test_get_raw_with_params(self, request_handler: Request) -> None:
        """Test get_raw passes query parameters correctly."""
        with respx.mock:
            route = respx.get("https://api.example.com/v1/search").mock(
                return_value=Response(
                    200,
                    json={
                        "data": {"concepts": []},
                        "meta": {"pagination": {"page": 2, "has_next": True}},
                    },
                )
            )

            result = request_handler.get_raw("/search", params={"query": "test", "page": 2})

            url_str = str(route.calls[0].request.url)
            assert "query=test" in url_str
            assert "page=2" in url_str
            assert result["meta"]["pagination"]["page"] == 2

    def test_get_raw_error_parsing(self, request_handler: Request) -> None:
        """Test get_raw raises errors correctly."""
        with respx.mock:
            respx.get("https://api.example.com/v1/test").mock(
                return_value=Response(
                    404,
                    json={"error": {"message": "Not found"}},
                    headers={"X-Request-Id": "req_123"},
                )
            )
            with pytest.raises(NotFoundError) as exc_info:
                request_handler.get_raw("/test")
            assert exc_info.value.request_id == "req_123"

    def test_get_raw_rate_limit(self, request_handler: Request) -> None:
        """Test get_raw handles rate limit with retry-after."""
        with respx.mock:
            respx.get("https://api.example.com/v1/test").mock(
                return_value=Response(
                    429,
                    json={"error": {"message": "Rate limited"}},
                    headers={"Retry-After": "45"},
                )
            )
            with pytest.raises(RateLimitError) as exc_info:
                request_handler.get_raw("/test")
            assert exc_info.value.retry_after == 45

    def test_get_raw_json_decode_error(self, request_handler: Request) -> None:
        """Test get_raw handles invalid JSON."""
        with respx.mock:
            respx.get("https://api.example.com/v1/test").mock(
                return_value=Response(200, content=b"not json")
            )
            with pytest.raises(OMOPHubError) as exc_info:
                request_handler.get_raw("/test")
            assert "Invalid JSON" in str(exc_info.value)


class TestAsyncRequest:
    """Tests for asynchronous AsyncRequest class."""

    @pytest.fixture
    def http_client(self) -> AsyncHTTPClientImpl:
        """Create async HTTP client for tests."""
        return AsyncHTTPClientImpl(max_retries=0)

    @pytest.fixture
    def request_handler(self, http_client: AsyncHTTPClientImpl) -> AsyncRequest:
        """Create async request handler for tests."""
        return AsyncRequest(
            http_client=http_client,
            base_url="https://api.example.com/v1",
            api_key="test_api_key",
        )

    @pytest.mark.asyncio
    async def test_async_get_request(self, request_handler: AsyncRequest) -> None:
        """Test async GET request."""
        with respx.mock:
            respx.get("https://api.example.com/v1/concepts/123").mock(
                return_value=Response(
                    200,
                    json={
                        "success": True,
                        "data": {"concept_id": 123, "concept_name": "Test"},
                    },
                )
            )

            result = await request_handler.get("/concepts/123")
            assert result["concept_id"] == 123

    @pytest.mark.asyncio
    async def test_async_get_with_params(self, request_handler: AsyncRequest) -> None:
        """Test async GET request with parameters."""
        with respx.mock:
            route = respx.get("https://api.example.com/v1/search").mock(
                return_value=Response(200, json={"success": True, "data": []})
            )

            await request_handler.get("/search", params={"query": "test"})

            assert "query=test" in str(route.calls[0].request.url)

    @pytest.mark.asyncio
    async def test_async_post_request(self, request_handler: AsyncRequest) -> None:
        """Test async POST request."""
        with respx.mock:
            respx.post("https://api.example.com/v1/concepts/batch").mock(
                return_value=Response(
                    200, json={"success": True, "data": {"concepts": []}}
                )
            )

            result = await request_handler.post(
                "/concepts/batch", json_data={"concept_ids": [1, 2]}
            )

            assert "concepts" in result

    @pytest.mark.asyncio
    async def test_async_auth_header(self, request_handler: AsyncRequest) -> None:
        """Test async request includes auth header."""
        with respx.mock:
            route = respx.get("https://api.example.com/v1/test").mock(
                return_value=Response(200, json={"success": True, "data": {}})
            )

            await request_handler.get("/test")

            assert "Authorization" in route.calls[0].request.headers
            assert (
                route.calls[0].request.headers["Authorization"] == "Bearer test_api_key"
            )

    @pytest.mark.asyncio
    async def test_async_vocab_version_header(self) -> None:
        """Test async request includes vocab version header."""
        http_client = AsyncHTTPClientImpl(max_retries=0)
        request_handler = AsyncRequest(
            http_client=http_client,
            base_url="https://api.example.com/v1",
            api_key="test_api_key",
            vocab_version="2025.1",
        )

        with respx.mock:
            route = respx.get("https://api.example.com/v1/test").mock(
                return_value=Response(200, json={"success": True, "data": {}})
            )

            await request_handler.get("/test")

            assert route.calls[0].request.headers["X-Vocab-Version"] == "2025.1"

    @pytest.mark.asyncio
    async def test_async_error_parsing(self, request_handler: AsyncRequest) -> None:
        """Test async error response parsing."""
        with respx.mock:
            respx.get("https://api.example.com/v1/test").mock(
                return_value=Response(
                    404,
                    json={
                        "success": False,
                        "error": {"message": "Not found"},
                    },
                    headers={"X-Request-Id": "req_xyz789"},
                )
            )

            with pytest.raises(NotFoundError) as exc_info:
                await request_handler.get("/test")

            assert exc_info.value.request_id == "req_xyz789"

    @pytest.mark.asyncio
    async def test_async_json_decode_error(self, request_handler: AsyncRequest) -> None:
        """Test async handling of invalid JSON."""
        with respx.mock:
            respx.get("https://api.example.com/v1/test").mock(
                return_value=Response(200, content=b"not valid json")
            )

            with pytest.raises(OMOPHubError) as exc_info:
                await request_handler.get("/test")

            assert "Invalid JSON" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_async_rate_limit_error(self, request_handler: AsyncRequest) -> None:
        """Test async 429 rate limit error with retry-after."""
        with respx.mock:
            respx.get("https://api.example.com/v1/test").mock(
                return_value=Response(
                    429,
                    json={"error": {"message": "Too many requests"}},
                    headers={"Retry-After": "30"},
                )
            )

            with pytest.raises(RateLimitError) as exc_info:
                await request_handler.get("/test")

            assert exc_info.value.retry_after == 30

    @pytest.mark.asyncio
    async def test_async_get_raw_request(self, request_handler: AsyncRequest) -> None:
        """Test async get_raw returns full response with data and meta."""
        with respx.mock:
            respx.get("https://api.example.com/v1/search").mock(
                return_value=Response(
                    200,
                    json={
                        "data": {"concepts": [{"concept_id": 42}]},
                        "meta": {"pagination": {"page": 1, "has_next": True, "total_pages": 3}},
                    },
                )
            )
            result = await request_handler.get_raw("/search")
            assert "data" in result
            assert "meta" in result
            assert result["meta"]["pagination"]["page"] == 1
            assert result["meta"]["pagination"]["has_next"] is True

    @pytest.mark.asyncio
    async def test_async_get_raw_with_params(self, request_handler: AsyncRequest) -> None:
        """Test async get_raw passes query parameters correctly."""
        with respx.mock:
            route = respx.get("https://api.example.com/v1/search").mock(
                return_value=Response(
                    200,
                    json={
                        "data": {"concepts": []},
                        "meta": {"pagination": {"page": 3}},
                    },
                )
            )

            result = await request_handler.get_raw("/search", params={"page": 3})

            url_str = str(route.calls[0].request.url)
            assert "page=3" in url_str
            assert result["meta"]["pagination"]["page"] == 3

    @pytest.mark.asyncio
    async def test_async_get_raw_error(self, request_handler: AsyncRequest) -> None:
        """Test async get_raw raises errors correctly."""
        with respx.mock:
            respx.get("https://api.example.com/v1/test").mock(
                return_value=Response(
                    404,
                    json={"error": {"message": "Not found"}},
                    headers={"X-Request-Id": "req_async_456"},
                )
            )
            with pytest.raises(NotFoundError) as exc_info:
                await request_handler.get_raw("/test")
            assert exc_info.value.request_id == "req_async_456"

    @pytest.mark.asyncio
    async def test_async_get_raw_rate_limit(self, request_handler: AsyncRequest) -> None:
        """Test async get_raw handles rate limit with retry-after."""
        with respx.mock:
            respx.get("https://api.example.com/v1/test").mock(
                return_value=Response(
                    429,
                    json={"error": {"message": "Rate limited"}},
                    headers={"Retry-After": "60"},
                )
            )
            with pytest.raises(RateLimitError) as exc_info:
                await request_handler.get_raw("/test")
            assert exc_info.value.retry_after == 60

    @pytest.mark.asyncio
    async def test_async_get_raw_json_decode_error(
        self, request_handler: AsyncRequest
    ) -> None:
        """Test async get_raw handles invalid JSON."""
        with respx.mock:
            respx.get("https://api.example.com/v1/test").mock(
                return_value=Response(200, content=b"invalid json response")
            )
            with pytest.raises(OMOPHubError) as exc_info:
                await request_handler.get_raw("/test")
            assert "Invalid JSON" in str(exc_info.value)
