"""Tests for the vocabularies resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import respx
from httpx import Response

if TYPE_CHECKING:
    import omophub
    from omophub import OMOPHub


class TestVocabulariesResource:
    """Tests for the synchronous Vocabularies resource."""

    @respx.mock
    def test_list_vocabularies(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test listing vocabularies."""
        vocabularies_response = {
            "success": True,
            "data": {
                "vocabularies": [
                    {
                        "vocabulary_id": "SNOMED",
                        "vocabulary_name": "Systematic Nomenclature of Medicine",
                        "vocabulary_concept_id": 44819096,
                    },
                    {
                        "vocabulary_id": "ICD10CM",
                        "vocabulary_name": "ICD-10-CM",
                        "vocabulary_concept_id": 44819097,
                    },
                ],
                "meta": {"pagination": {"total_items": 2}},
            },
        }
        respx.get(f"{base_url}/vocabularies").mock(
            return_value=Response(200, json=vocabularies_response)
        )

        result = sync_client.vocabularies.list()
        assert "vocabularies" in result

    @respx.mock
    def test_list_vocabularies_with_options(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Test listing vocabularies with all options."""
        route = respx.get(f"{base_url}/vocabularies").mock(
            return_value=Response(
                200, json={"success": True, "data": {"vocabularies": []}}
            )
        )

        sync_client.vocabularies.list(
            include_stats=True,
            include_inactive=True,
            sort_by="priority",
            sort_order="desc",
            page=2,
            page_size=50,
        )

        url_str = str(route.calls[0].request.url)
        assert "include_stats=true" in url_str
        assert "include_inactive=true" in url_str
        assert "sort_by=priority" in url_str
        assert "sort_order=desc" in url_str
        assert "page=2" in url_str
        assert "page_size=50" in url_str

    @respx.mock
    def test_get_vocabulary(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test getting a specific vocabulary."""
        vocabulary_response = {
            "success": True,
            "data": {
                "vocabulary_id": "SNOMED",
                "vocabulary_name": "Systematic Nomenclature of Medicine",
                "vocabulary_version": "2024-01-01",
            },
        }
        respx.get(f"{base_url}/vocabularies/SNOMED").mock(
            return_value=Response(200, json=vocabulary_response)
        )

        result = sync_client.vocabularies.get("SNOMED")
        assert result["vocabulary_id"] == "SNOMED"

    @respx.mock
    def test_get_vocabulary_with_options(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Test getting vocabulary with include options."""
        route = respx.get(f"{base_url}/vocabularies/SNOMED").mock(
            return_value=Response(
                200, json={"success": True, "data": {"vocabulary_id": "SNOMED"}}
            )
        )

        sync_client.vocabularies.get(
            "SNOMED",
            include_stats=True,
            include_domains=True,
        )

        url_str = str(route.calls[0].request.url)
        assert "include_stats=true" in url_str
        assert "include_domains=true" in url_str

    @respx.mock
    def test_get_vocabulary_stats(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test getting vocabulary statistics."""
        stats_response = {
            "success": True,
            "data": {
                "vocabulary_id": "SNOMED",
                "total_concepts": 450000,
                "standard_concepts": 350000,
                "non_standard_concepts": 100000,
            },
        }
        respx.get(f"{base_url}/vocabularies/SNOMED/stats").mock(
            return_value=Response(200, json=stats_response)
        )

        result = sync_client.vocabularies.stats("SNOMED")
        assert result["vocabulary_id"] == "SNOMED"

    @respx.mock
    def test_get_vocabulary_domains(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test getting vocabulary domains."""
        domains_response = {
            "success": True,
            "data": {
                "domains": [
                    {"domain_id": "Condition", "concept_count": 150000},
                    {"domain_id": "Drug", "concept_count": 100000},
                ],
            },
        }
        route = respx.get(f"{base_url}/vocabularies/domains").mock(
            return_value=Response(200, json=domains_response)
        )

        result = sync_client.vocabularies.domains(
            vocabulary_ids=["SNOMED"], page=1, page_size=25
        )

        assert "domains" in result
        url_str = str(route.calls[0].request.url)
        assert "vocabulary_ids=SNOMED" in url_str
        assert "page=1" in url_str
        assert "page_size=25" in url_str

    @respx.mock
    def test_get_vocabulary_concepts(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test getting concepts in a vocabulary."""
        concepts_response = {
            "success": True,
            "data": {
                "concepts": [
                    {"concept_id": 201826, "concept_name": "Type 2 diabetes mellitus"},
                ],
                "meta": {"pagination": {"total_items": 1}},
            },
        }
        route = respx.get(f"{base_url}/vocabularies/SNOMED/concepts").mock(
            return_value=Response(200, json=concepts_response)
        )

        sync_client.vocabularies.concepts(
            "SNOMED",
            domain_id="Condition",
            concept_class_id="Clinical Finding",
            standard_only=True,
            page=1,
            page_size=100,
        )

        url_str = str(route.calls[0].request.url)
        assert "domain_id=Condition" in url_str
        assert "concept_class_id=Clinical+Finding" in url_str
        assert "standard_only=true" in url_str


class TestAsyncVocabulariesResource:
    """Tests for the asynchronous AsyncVocabularies resource."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_list_vocabularies(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async listing vocabularies."""
        respx.get(f"{base_url}/vocabularies").mock(
            return_value=Response(
                200, json={"success": True, "data": {"vocabularies": []}}
            )
        )

        result = await async_client.vocabularies.list()
        assert "vocabularies" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_list_vocabularies_with_options(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async listing with options."""
        route = respx.get(f"{base_url}/vocabularies").mock(
            return_value=Response(
                200, json={"success": True, "data": {"vocabularies": []}}
            )
        )

        await async_client.vocabularies.list(
            include_stats=True,
            include_inactive=True,
            sort_by="updated",
            sort_order="desc",
        )

        url_str = str(route.calls[0].request.url)
        assert "include_stats=true" in url_str
        assert "include_inactive=true" in url_str
        assert "sort_by=updated" in url_str
        assert "sort_order=desc" in url_str

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_vocabulary(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async getting a vocabulary."""
        respx.get(f"{base_url}/vocabularies/ICD10CM").mock(
            return_value=Response(
                200, json={"success": True, "data": {"vocabulary_id": "ICD10CM"}}
            )
        )

        result = await async_client.vocabularies.get("ICD10CM")
        assert result["vocabulary_id"] == "ICD10CM"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_vocabulary_with_options(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async get vocabulary with options."""
        route = respx.get(f"{base_url}/vocabularies/SNOMED").mock(
            return_value=Response(
                200, json={"success": True, "data": {"vocabulary_id": "SNOMED"}}
            )
        )

        await async_client.vocabularies.get(
            "SNOMED",
            include_stats=True,
            include_domains=True,
        )

        url_str = str(route.calls[0].request.url)
        assert "include_stats=true" in url_str
        assert "include_domains=true" in url_str

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_vocabulary_stats(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async getting vocabulary stats."""
        respx.get(f"{base_url}/vocabularies/SNOMED/stats").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "data": {"vocabulary_id": "SNOMED", "total_concepts": 450000},
                },
            )
        )

        result = await async_client.vocabularies.stats("SNOMED")
        assert result["vocabulary_id"] == "SNOMED"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_vocabulary_domains(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async getting vocabulary domains."""
        route = respx.get(f"{base_url}/vocabularies/domains").mock(
            return_value=Response(
                200, json={"success": True, "data": {"domains": []}}
            )
        )

        await async_client.vocabularies.domains(
            vocabulary_ids=["SNOMED"], page=2, page_size=30
        )

        url_str = str(route.calls[0].request.url)
        assert "vocabulary_ids=SNOMED" in url_str
        assert "page=2" in url_str
        assert "page_size=30" in url_str

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_vocabulary_concepts(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async getting vocabulary concepts."""
        route = respx.get(f"{base_url}/vocabularies/SNOMED/concepts").mock(
            return_value=Response(
                200, json={"success": True, "data": {"concepts": []}}
            )
        )

        await async_client.vocabularies.concepts(
            "SNOMED",
            domain_id="Drug",
            concept_class_id="Ingredient",
            standard_only=True,
            page=1,
            page_size=50,
        )

        url_str = str(route.calls[0].request.url)
        assert "domain_id=Drug" in url_str
        assert "concept_class_id=Ingredient" in url_str
        assert "standard_only=true" in url_str
