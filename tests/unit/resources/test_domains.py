"""Tests for the domains resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import respx
from httpx import Response

if TYPE_CHECKING:
    import omophub
    from omophub import OMOPHub


class TestDomainsResource:
    """Tests for the synchronous Domains resource."""

    @respx.mock
    def test_list_domains(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test listing all domains."""
        domains_response = {
            "success": True,
            "data": {
                "domains": [
                    {"domain_id": "Condition", "domain_name": "Condition"},
                    {"domain_id": "Drug", "domain_name": "Drug"},
                    {"domain_id": "Procedure", "domain_name": "Procedure"},
                ],
            },
        }
        respx.get(f"{base_url}/domains").mock(
            return_value=Response(200, json=domains_response)
        )

        result = sync_client.domains.list()
        assert "domains" in result

    @respx.mock
    def test_list_domains_with_stats(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test listing domains with include_stats option."""
        route = respx.get(f"{base_url}/domains").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "data": {
                        "domains": [
                            {
                                "domain_id": "Condition",
                                "domain_name": "Condition",
                                "concept_count": 845672,
                                "standard_concept_count": 423891,
                                "vocabulary_coverage": ["SNOMED", "ICD10CM"],
                            }
                        ]
                    },
                },
            )
        )

        sync_client.domains.list(include_stats=True)

        url_str = str(route.calls[0].request.url)
        assert "include_stats=true" in url_str

    @respx.mock
    def test_list_domains_without_stats(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Test listing domains without stats (default)."""
        route = respx.get(f"{base_url}/domains").mock(
            return_value=Response(200, json={"success": True, "data": {"domains": []}})
        )

        sync_client.domains.list()

        url_str = str(route.calls[0].request.url)
        # Should not include include_stats when False (default)
        assert "include_stats" not in url_str

    @respx.mock
    def test_get_domain_concepts(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test getting concepts in a domain."""
        concepts_response = {
            "success": True,
            "data": {
                "concepts": [
                    {"concept_id": 201826, "concept_name": "Type 2 diabetes mellitus"},
                    {"concept_id": 4329847, "concept_name": "Myocardial infarction"},
                ],
                "meta": {"pagination": {"total_items": 2, "has_next": False}},
            },
        }
        route = respx.get(f"{base_url}/domains/Condition/concepts").mock(
            return_value=Response(200, json=concepts_response)
        )

        result = sync_client.domains.concepts(
            "Condition",
            vocabulary_ids=["SNOMED"],
            standard_only=True,
            include_invalid=True,
            page=1,
            page_size=100,
        )

        assert "concepts" in result
        url_str = str(route.calls[0].request.url)
        assert "vocabulary_ids=SNOMED" in url_str
        assert "standard_only=true" in url_str
        assert "include_invalid=true" in url_str
        assert "page=1" in url_str
        assert "page_size=100" in url_str


class TestAsyncDomainsResource:
    """Tests for the asynchronous AsyncDomains resource."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_list_domains(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async listing domains."""
        respx.get(f"{base_url}/domains").mock(
            return_value=Response(200, json={"success": True, "data": {"domains": []}})
        )

        result = await async_client.domains.list()
        assert "domains" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_list_domains_with_stats(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async listing domains with include_stats."""
        route = respx.get(f"{base_url}/domains").mock(
            return_value=Response(200, json={"success": True, "data": {"domains": []}})
        )

        await async_client.domains.list(include_stats=True)

        url_str = str(route.calls[0].request.url)
        assert "include_stats=true" in url_str

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_domain_concepts(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async getting domain concepts."""
        route = respx.get(f"{base_url}/domains/Condition/concepts").mock(
            return_value=Response(200, json={"success": True, "data": {"concepts": []}})
        )

        await async_client.domains.concepts(
            "Condition",
            vocabulary_ids=["SNOMED", "ICD10CM"],
            standard_only=True,
            include_invalid=True,
            page=2,
            page_size=25,
        )

        url_str = str(route.calls[0].request.url)
        assert "vocabulary_ids=SNOMED%2CICD10CM" in url_str
        assert "standard_only=true" in url_str
        assert "include_invalid=true" in url_str
        assert "page=2" in url_str
        assert "page_size=25" in url_str
