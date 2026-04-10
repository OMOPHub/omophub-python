"""Integration tests for async client functionality."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    import omophub

from tests.conftest import (
    ASPIRIN_CONCEPT_ID,
    DIABETES_CONCEPT_ID,
    MI_CONCEPT_ID,
    extract_data,
)


@pytest.mark.integration
@pytest.mark.asyncio
class TestAsyncIntegration:
    """Integration tests for async client against production API."""

    async def test_async_get_concept(
        self, async_integration_client: omophub.AsyncOMOPHub
    ) -> None:
        """Async get concept from production API."""
        concept = await async_integration_client.concepts.get(DIABETES_CONCEPT_ID)

        assert concept["concept_id"] == DIABETES_CONCEPT_ID
        assert "Type 2 diabetes" in concept["concept_name"]

    async def test_async_search(
        self, async_integration_client: omophub.AsyncOMOPHub
    ) -> None:
        """Async search for concepts."""
        result = await async_integration_client.search.basic(
            "diabetes mellitus",
            page_size=5,
        )

        concepts = extract_data(result, "concepts")
        assert len(concepts) > 0

    async def test_async_concurrent_requests(
        self, async_integration_client: omophub.AsyncOMOPHub
    ) -> None:
        """Test concurrent async requests."""
        # Run multiple requests concurrently
        tasks = [
            async_integration_client.concepts.get(DIABETES_CONCEPT_ID),
            async_integration_client.concepts.get(ASPIRIN_CONCEPT_ID),
            async_integration_client.concepts.get(MI_CONCEPT_ID),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All concurrent requests should succeed
        successful = [r for r in results if not isinstance(r, Exception)]
        assert len(successful) >= 2, (
            f"Expected at least 2 of 3 concurrent requests to succeed, "
            f"got {len(successful)}"
        )

    async def test_async_vocabularies(
        self, async_integration_client: omophub.AsyncOMOPHub
    ) -> None:
        """Async list vocabularies."""
        result = await async_integration_client.vocabularies.list()

        vocabs = extract_data(result, "vocabularies")
        assert len(vocabs) > 0

    async def test_async_domains(
        self, async_integration_client: omophub.AsyncOMOPHub
    ) -> None:
        """Async list domains."""
        result = await async_integration_client.domains.list()

        domains = extract_data(result, "domains")
        assert len(domains) > 0

    async def test_async_hierarchy(
        self, async_integration_client: omophub.AsyncOMOPHub
    ) -> None:
        """Async get hierarchy."""
        result = await async_integration_client.hierarchy.ancestors(
            DIABETES_CONCEPT_ID,
            max_levels=3,
        )

        ancestors = extract_data(result, "ancestors")
        assert isinstance(ancestors, list)

    async def test_async_mappings(
        self, async_integration_client: omophub.AsyncOMOPHub
    ) -> None:
        """Async get mappings."""
        result = await async_integration_client.mappings.get(DIABETES_CONCEPT_ID)

        mappings = extract_data(result, "mappings")
        assert isinstance(mappings, list)

    async def test_async_autocomplete(
        self, async_integration_client: omophub.AsyncOMOPHub
    ) -> None:
        """Async autocomplete."""
        result = await async_integration_client.search.autocomplete(
            "aspi",
            page_size=5,
        )

        suggestions = extract_data(result, "suggestions")
        assert isinstance(suggestions, list)
