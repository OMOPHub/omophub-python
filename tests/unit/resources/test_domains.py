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
                "summary": {"total_domains": 3},
            },
        }
        respx.get(f"{base_url}/domains").mock(
            return_value=Response(200, json=domains_response)
        )

        result = sync_client.domains.list()
        assert "domains" in result

    @respx.mock
    def test_list_domains_with_options(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Test listing domains with all filter options."""
        route = respx.get(f"{base_url}/domains").mock(
            return_value=Response(
                200, json={"success": True, "data": {"domains": []}}
            )
        )

        sync_client.domains.list(
            vocabulary_ids=["SNOMED", "ICD10CM"],
            include_concept_counts=True,
            include_statistics=True,
            include_examples=True,
            standard_only=True,
            active_only=False,
            sort_by="concept_count",
            sort_order="desc",
        )

        url_str = str(route.calls[0].request.url)
        assert "vocabulary_ids=SNOMED%2CICD10CM" in url_str
        assert "include_concept_counts=true" in url_str
        assert "include_statistics=true" in url_str
        assert "include_examples=true" in url_str
        assert "standard_only=true" in url_str
        assert "active_only=false" in url_str
        assert "sort_by=concept_count" in url_str
        assert "sort_order=desc" in url_str

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
            concept_class_ids=["Clinical Finding"],
            standard_only=True,
            page=1,
            page_size=100,
        )

        assert "concepts" in result
        url_str = str(route.calls[0].request.url)
        assert "vocabulary_ids=SNOMED" in url_str
        assert "concept_class_ids=Clinical+Finding" in url_str
        assert "standard_only=true" in url_str
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
            return_value=Response(
                200, json={"success": True, "data": {"domains": []}}
            )
        )

        result = await async_client.domains.list()
        assert "domains" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_list_domains_with_options(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async listing domains with all options."""
        route = respx.get(f"{base_url}/domains").mock(
            return_value=Response(
                200, json={"success": True, "data": {"domains": []}}
            )
        )

        await async_client.domains.list(
            vocabulary_ids=["SNOMED"],
            include_concept_counts=True,
            include_statistics=True,
            include_examples=True,
            standard_only=True,
            active_only=False,
            sort_by="domain_id",
            sort_order="asc",
        )

        url_str = str(route.calls[0].request.url)
        assert "vocabulary_ids=SNOMED" in url_str
        assert "include_concept_counts=true" in url_str
        assert "include_statistics=true" in url_str
        assert "include_examples=true" in url_str
        assert "active_only=false" in url_str
        assert "standard_only=true" in url_str
        assert "sort_by=domain_id" in url_str
        assert "sort_order=asc" in url_str

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_domain_concepts(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async getting domain concepts."""
        route = respx.get(f"{base_url}/domains/Condition/concepts").mock(
            return_value=Response(
                200, json={"success": True, "data": {"concepts": []}}
            )
        )

        await async_client.domains.concepts(
            "Condition",
            vocabulary_ids=["SNOMED", "ICD10CM"],
            concept_class_ids=["Clinical Finding", "Disease"],
            standard_only=True,
            page=2,
            page_size=25,
        )

        url_str = str(route.calls[0].request.url)
        assert "vocabulary_ids=SNOMED%2CICD10CM" in url_str
        assert "concept_class_ids=Clinical+Finding%2CDisease" in url_str
        assert "standard_only=true" in url_str
        assert "page=2" in url_str
        assert "page_size=25" in url_str
