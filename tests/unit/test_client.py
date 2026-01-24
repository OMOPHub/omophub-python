"""Tests for the OMOPHub client."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

import omophub
from omophub import AuthenticationError, OMOPHub


class TestOMOPHubClient:
    """Tests for the synchronous OMOPHub client."""

    def test_client_requires_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that client raises error without API key."""
        monkeypatch.setattr("omophub._client.default_api_key", None)

        with pytest.raises(AuthenticationError):
            OMOPHub()

    def test_client_accepts_api_key(self, api_key: str) -> None:
        """Test that client accepts API key parameter."""
        client = OMOPHub(api_key=api_key)
        assert client._api_key == api_key

    def test_client_has_resources(self, sync_client: OMOPHub) -> None:
        """Test that client has all expected resources."""
        assert hasattr(sync_client, "concepts")
        assert hasattr(sync_client, "search")
        assert hasattr(sync_client, "hierarchy")
        assert hasattr(sync_client, "relationships")
        assert hasattr(sync_client, "mappings")
        assert hasattr(sync_client, "vocabularies")
        assert hasattr(sync_client, "domains")

    def test_client_context_manager(self, api_key: str) -> None:
        """Test client as context manager."""
        with OMOPHub(api_key=api_key) as client:
            assert client._api_key == api_key

    @respx.mock
    def test_get_concept(
        self, sync_client: OMOPHub, mock_api_response: dict, base_url: str
    ) -> None:
        """Test getting a concept by ID."""
        respx.get(f"{base_url}/concepts/201826").mock(
            return_value=Response(200, json=mock_api_response)
        )

        concept = sync_client.concepts.get(201826)
        assert concept["concept_id"] == 201826
        assert concept["concept_name"] == "Type 2 diabetes mellitus"


class TestAsyncOMOPHubClient:
    """Tests for the asynchronous OMOPHub client."""

    @pytest.mark.asyncio
    async def test_async_client_context_manager(self, api_key: str) -> None:
        """Test async client as context manager."""
        async with omophub.AsyncOMOPHub(api_key=api_key) as client:
            assert client._api_key == api_key

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_concept(
        self, async_client: omophub.AsyncOMOPHub, mock_api_response: dict, base_url: str
    ) -> None:
        """Test async getting a concept by ID."""
        respx.get(f"{base_url}/concepts/201826").mock(
            return_value=Response(200, json=mock_api_response)
        )

        concept = await async_client.concepts.get(201826)
        assert concept["concept_id"] == 201826

    def test_async_client_has_resources(
        self, async_client: omophub.AsyncOMOPHub
    ) -> None:
        """Test that async client has all expected resources."""
        assert hasattr(async_client, "concepts")
        assert hasattr(async_client, "search")
        assert hasattr(async_client, "hierarchy")
        assert hasattr(async_client, "relationships")
        assert hasattr(async_client, "mappings")
        assert hasattr(async_client, "vocabularies")
        assert hasattr(async_client, "domains")

    def test_async_client_requires_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that async client raises error without API key."""
        monkeypatch.setattr("omophub._client.default_api_key", None)

        with pytest.raises(AuthenticationError):
            omophub.AsyncOMOPHub()


class TestClientLazyPropertyCaching:
    """Tests for lazy property caching in clients."""

    def test_sync_client_lazy_property_caching(self, api_key: str) -> None:
        """Test that sync client caches resource instances."""
        client = OMOPHub(api_key=api_key)

        # Access concepts multiple times
        concepts1 = client.concepts
        concepts2 = client.concepts

        # Should be the same instance (cached)
        assert concepts1 is concepts2

        # Same for other resources
        search1 = client.search
        search2 = client.search
        assert search1 is search2

        hierarchy1 = client.hierarchy
        hierarchy2 = client.hierarchy
        assert hierarchy1 is hierarchy2

        relationships1 = client.relationships
        relationships2 = client.relationships
        assert relationships1 is relationships2

        mappings1 = client.mappings
        mappings2 = client.mappings
        assert mappings1 is mappings2

        vocabularies1 = client.vocabularies
        vocabularies2 = client.vocabularies
        assert vocabularies1 is vocabularies2

        domains1 = client.domains
        domains2 = client.domains
        assert domains1 is domains2

        client.close()

    @pytest.mark.asyncio
    async def test_async_client_lazy_property_caching(self, api_key: str) -> None:
        """Test that async client caches resource instances."""
        client = omophub.AsyncOMOPHub(api_key=api_key)

        # Access resources multiple times
        concepts1 = client.concepts
        concepts2 = client.concepts
        assert concepts1 is concepts2

        search1 = client.search
        search2 = client.search
        assert search1 is search2

        hierarchy1 = client.hierarchy
        hierarchy2 = client.hierarchy
        assert hierarchy1 is hierarchy2

        relationships1 = client.relationships
        relationships2 = client.relationships
        assert relationships1 is relationships2

        mappings1 = client.mappings
        mappings2 = client.mappings
        assert mappings1 is mappings2

        vocabularies1 = client.vocabularies
        vocabularies2 = client.vocabularies
        assert vocabularies1 is vocabularies2

        domains1 = client.domains
        domains2 = client.domains
        assert domains1 is domains2

        await client.close()


class TestClientConfiguration:
    """Tests for client configuration options."""

    def test_client_custom_timeout(self, api_key: str) -> None:
        """Test client accepts custom timeout."""
        client = OMOPHub(api_key=api_key, timeout=60.0)

        assert client._timeout == 60.0
        assert client._http_client._timeout == 60.0

        client.close()

    def test_client_custom_max_retries(self, api_key: str) -> None:
        """Test client accepts custom max_retries."""
        client = OMOPHub(api_key=api_key, max_retries=5)

        assert client._max_retries == 5
        assert client._http_client._max_retries == 5

        client.close()

    def test_client_vocab_version(self, api_key: str) -> None:
        """Test client accepts vocab_version parameter."""
        client = OMOPHub(api_key=api_key, vocab_version="2024.4")

        assert client._vocab_version == "2024.4"
        # Verify it's passed to request handler
        assert client._request._vocab_version == "2024.4"

        client.close()

    def test_client_custom_base_url(self, api_key: str) -> None:
        """Test client accepts custom base_url."""
        custom_url = "https://custom.api.com/v2"
        client = OMOPHub(api_key=api_key, base_url=custom_url)

        assert client._base_url == custom_url

        client.close()

    def test_client_base_url_trailing_slash_removed(self, api_key: str) -> None:
        """Test client removes trailing slash from base_url."""
        client = OMOPHub(api_key=api_key, base_url="https://api.example.com/v1/")

        assert client._base_url == "https://api.example.com/v1"

        client.close()

    @pytest.mark.asyncio
    async def test_async_client_custom_timeout(self, api_key: str) -> None:
        """Test async client accepts custom timeout."""
        client = omophub.AsyncOMOPHub(api_key=api_key, timeout=90.0)

        assert client._timeout == 90.0
        assert client._http_client._timeout == 90.0

        await client.close()

    @pytest.mark.asyncio
    async def test_async_client_vocab_version(self, api_key: str) -> None:
        """Test async client accepts vocab_version parameter."""
        client = omophub.AsyncOMOPHub(api_key=api_key, vocab_version="2025.1")

        assert client._vocab_version == "2025.1"
        assert client._request._vocab_version == "2025.1"

        await client.close()


class TestClientContextManagers:
    """Tests for client context manager functionality."""

    def test_sync_context_manager_closes_client(self, api_key: str) -> None:
        """Test sync client context manager closes resources."""
        with OMOPHub(api_key=api_key) as client:
            # Force client creation
            _ = client._http_client._get_client()
            assert client._http_client._client is not None

        # After exiting context, client should be closed
        assert client._http_client._client is None

    @pytest.mark.asyncio
    async def test_async_context_manager_closes_client(self, api_key: str) -> None:
        """Test async client context manager closes resources."""
        async with omophub.AsyncOMOPHub(api_key=api_key) as client:
            # Force client creation
            _ = await client._http_client._get_client()
            assert client._http_client._client is not None

        # After exiting context, client should be closed
        assert client._http_client._client is None

    def test_sync_close_is_idempotent(self, api_key: str) -> None:
        """Test sync client close can be called multiple times."""
        client = OMOPHub(api_key=api_key)
        client.close()
        client.close()  # Should not raise

    @pytest.mark.asyncio
    async def test_async_close_is_idempotent(self, api_key: str) -> None:
        """Test async client close can be called multiple times."""
        client = omophub.AsyncOMOPHub(api_key=api_key)
        await client.close()
        await client.close()  # Should not raise
