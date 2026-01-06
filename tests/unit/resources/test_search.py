"""Tests for the search resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import respx
from httpx import Response

if TYPE_CHECKING:
    import omophub
    from omophub import OMOPHub


class TestSearchResource:
    """Tests for the synchronous Search resource."""

    @respx.mock
    def test_basic_search(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test basic concept search."""
        search_response = {
            "success": True,
            "data": {
                "concepts": [
                    {"concept_id": 201826, "concept_name": "Type 2 diabetes mellitus"},
                ],
                "meta": {"pagination": {"total_items": 1, "has_next": False}},
            },
        }
        respx.get(f"{base_url}/search/concepts").mock(
            return_value=Response(200, json=search_response)
        )

        result = sync_client.search.basic("diabetes")
        assert "concepts" in result

    @respx.mock
    def test_basic_search_with_filters(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test basic search with vocabulary and domain filters."""
        route = respx.get(f"{base_url}/search/concepts").mock(
            return_value=Response(
                200, json={"success": True, "data": {"concepts": []}}
            )
        )

        sync_client.search.basic(
            "diabetes",
            vocabulary_ids=["SNOMED", "ICD10CM"],
            domain_ids=["Condition"],
            concept_class_ids=["Clinical Finding"],
            standard_concept="S",
            include_synonyms=True,
            include_invalid=True,
            min_score=0.5,
            exact_match=True,
            page=2,
            page_size=50,
            sort_by="concept_name",
            sort_order="desc",
        )

        url_str = str(route.calls[0].request.url)
        assert "vocabulary_ids=SNOMED%2CICD10CM" in url_str
        assert "domain_ids=Condition" in url_str
        assert "concept_class_ids=Clinical+Finding" in url_str
        assert "standard_concept=S" in url_str
        assert "include_synonyms=true" in url_str
        assert "include_invalid=true" in url_str
        assert "min_score=0.5" in url_str
        assert "exact_match=true" in url_str
        assert "page=2" in url_str
        assert "page_size=50" in url_str
        assert "sort_by=concept_name" in url_str
        assert "sort_order=desc" in url_str

    @respx.mock
    def test_basic_iter_single_page(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test basic_iter with single page of results."""
        search_response = {
            "success": True,
            "data": {
                "concepts": [
                    {"concept_id": 201826, "concept_name": "Type 2 diabetes mellitus"},
                    {"concept_id": 201820, "concept_name": "Diabetes mellitus"},
                ],
                "meta": {"pagination": {"page": 1, "has_next": False}},
            },
        }
        respx.get(f"{base_url}/search/concepts").mock(
            return_value=Response(200, json=search_response)
        )

        concepts = list(sync_client.search.basic_iter("diabetes"))
        assert len(concepts) == 2

    @respx.mock
    def test_basic_iter_multiple_pages(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test basic_iter auto-pagination across multiple pages."""
        page1_response = {
            "success": True,
            "data": {
                "concepts": [{"concept_id": 1}],
                "meta": {"pagination": {"page": 1, "has_next": True}},
            },
        }
        page2_response = {
            "success": True,
            "data": {
                "concepts": [{"concept_id": 2}],
                "meta": {"pagination": {"page": 2, "has_next": False}},
            },
        }

        call_count = 0

        def mock_response(request):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return Response(200, json=page1_response)
            return Response(200, json=page2_response)

        respx.get(f"{base_url}/search/concepts").mock(side_effect=mock_response)

        concepts = list(sync_client.search.basic_iter("diabetes", page_size=1))
        assert len(concepts) == 2
        assert concepts[0]["concept_id"] == 1
        assert concepts[1]["concept_id"] == 2

    @respx.mock
    def test_advanced_search(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test advanced search with POST body."""
        route = respx.post(f"{base_url}/search/advanced").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "data": {"concepts": [], "facets": {}},
                },
            )
        )

        sync_client.search.advanced(
            "myocardial infarction",
            vocabulary_ids=["SNOMED"],
            domain_ids=["Condition"],
            concept_class_ids=["Clinical Finding"],
            standard_concepts_only=True,
            include_invalid=True,
            relationship_filters=[{"type": "Is a", "concept_id": 123}],
            page=2,
            page_size=50,
        )

        # Verify POST body was sent
        assert route.calls[0].request.content

    @respx.mock
    def test_autocomplete(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test autocomplete suggestions."""
        autocomplete_response = {
            "success": True,
            "data": [
                {"suggestion": "diabetes mellitus", "type": "concept_name"},
                {"suggestion": "diabetic", "type": "concept_name"},
            ],
        }
        route = respx.get(f"{base_url}/search/suggest").mock(
            return_value=Response(200, json=autocomplete_response)
        )

        result = sync_client.search.autocomplete(
            "diab",
            vocabulary_ids=["SNOMED"],
            domains=["Condition"],
            page_size=5,
        )

        assert len(result) == 2
        url_str = str(route.calls[0].request.url)
        assert "query=diab" in url_str
        assert "vocabulary_ids=SNOMED" in url_str
        assert "domains=Condition" in url_str
        assert "page_size=5" in url_str


class TestAsyncSearchResource:
    """Tests for the asynchronous AsyncSearch resource."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_basic_search(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async basic search."""
        search_response = {
            "success": True,
            "data": {
                "concepts": [{"concept_id": 201826}],
            },
        }
        respx.get(f"{base_url}/search/concepts").mock(
            return_value=Response(200, json=search_response)
        )

        result = await async_client.search.basic("diabetes")
        assert "concepts" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_basic_search_with_filters(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async basic search with all filters."""
        route = respx.get(f"{base_url}/search/concepts").mock(
            return_value=Response(
                200, json={"success": True, "data": {"concepts": []}}
            )
        )

        await async_client.search.basic(
            "diabetes",
            vocabulary_ids=["SNOMED"],
            domain_ids=["Condition"],
            concept_class_ids=["Clinical Finding"],
            standard_concept="S",
            include_synonyms=True,
            include_invalid=True,
            min_score=0.8,
            exact_match=True,
            page=1,
            page_size=25,
            sort_by="relevance",
            sort_order="desc",
        )

        url_str = str(route.calls[0].request.url)
        assert "vocabulary_ids=SNOMED" in url_str
        assert "standard_concept=S" in url_str
        assert "include_synonyms=true" in url_str
        assert "min_score=0.8" in url_str

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_advanced_search(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async advanced search."""
        respx.post(f"{base_url}/search/advanced").mock(
            return_value=Response(
                200, json={"success": True, "data": {"concepts": []}}
            )
        )

        result = await async_client.search.advanced(
            "heart attack",
            vocabulary_ids=["SNOMED", "ICD10CM"],
            domain_ids=["Condition"],
            standard_concepts_only=True,
        )

        assert "concepts" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_autocomplete(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async autocomplete."""
        autocomplete_response = {
            "success": True,
            "data": [{"suggestion": "aspirin", "type": "concept_name"}],
        }
        respx.get(f"{base_url}/search/suggest").mock(
            return_value=Response(200, json=autocomplete_response)
        )

        result = await async_client.search.autocomplete("asp")
        assert len(result) == 1
