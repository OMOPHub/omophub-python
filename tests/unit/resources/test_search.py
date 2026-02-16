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
    def test_basic_search_with_filters(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Test basic search with vocabulary and domain filters."""
        route = respx.get(f"{base_url}/search/concepts").mock(
            return_value=Response(200, json={"success": True, "data": {"concepts": []}})
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
        # Note: meta is at top level, not nested inside data
        search_response = {
            "success": True,
            "data": [
                {"concept_id": 201826, "concept_name": "Type 2 diabetes mellitus"},
                {"concept_id": 201820, "concept_name": "Diabetes mellitus"},
            ],
            "meta": {"pagination": {"page": 1, "has_next": False}},
        }
        respx.get(f"{base_url}/search/concepts").mock(
            return_value=Response(200, json=search_response)
        )

        concepts = list(sync_client.search.basic_iter("diabetes"))
        assert len(concepts) == 2

    @respx.mock
    def test_basic_iter_multiple_pages(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Test basic_iter auto-pagination across multiple pages."""
        # Note: meta is at top level, not nested inside data
        page1_response = {
            "success": True,
            "data": [{"concept_id": 1}],
            "meta": {"pagination": {"page": 1, "has_next": True}},
        }
        page2_response = {
            "success": True,
            "data": [{"concept_id": 2}],
            "meta": {"pagination": {"page": 2, "has_next": False}},
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
            return_value=Response(200, json={"success": True, "data": {"concepts": []}})
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
            return_value=Response(200, json={"success": True, "data": {"concepts": []}})
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


class TestSemanticSearch:
    """Tests for semantic search functionality."""

    @respx.mock
    def test_semantic_search(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test semantic concept search."""
        semantic_response = {
            "success": True,
            "data": {
                "results": [
                    {
                        "concept_id": 4329847,
                        "concept_name": "Myocardial infarction",
                        "domain_id": "Condition",
                        "vocabulary_id": "SNOMED",
                        "concept_class_id": "Clinical Finding",
                        "standard_concept": "S",
                        "concept_code": "22298006",
                        "similarity_score": 0.95,
                        "matched_text": "heart attack",
                    }
                ],
            },
            "meta": {"pagination": {"page": 1, "has_next": False, "total_items": 1}},
        }
        route = respx.get(f"{base_url}/concepts/semantic-search").mock(
            return_value=Response(200, json=semantic_response)
        )

        result = sync_client.search.semantic("heart attack")
        assert "results" in result
        assert len(result["results"]) == 1
        assert result["results"][0]["similarity_score"] == 0.95

        url_str = str(route.calls[0].request.url)
        assert "query=heart+attack" in url_str

    @respx.mock
    def test_semantic_search_with_filters(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Test semantic search with all filters."""
        route = respx.get(f"{base_url}/concepts/semantic-search").mock(
            return_value=Response(200, json={"success": True, "data": {"results": []}})
        )

        sync_client.search.semantic(
            "heart attack",
            vocabulary_ids=["SNOMED", "ICD10CM"],
            domain_ids=["Condition"],
            standard_concept="S",
            concept_class_id="Clinical Finding",
            threshold=0.5,
            page=2,
            page_size=50,
        )

        url_str = str(route.calls[0].request.url)
        assert "vocabulary_ids=SNOMED%2CICD10CM" in url_str
        assert "domain_ids=Condition" in url_str
        assert "standard_concept=S" in url_str
        assert "concept_class_id=Clinical+Finding" in url_str
        assert "threshold=0.5" in url_str
        assert "page=2" in url_str
        assert "page_size=50" in url_str

    @respx.mock
    def test_semantic_iter_single_page(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Test semantic_iter with single page."""
        semantic_response = {
            "success": True,
            "data": [
                {"concept_id": 1, "similarity_score": 0.9},
                {"concept_id": 2, "similarity_score": 0.8},
            ],
            "meta": {"pagination": {"page": 1, "has_next": False}},
        }
        respx.get(f"{base_url}/concepts/semantic-search").mock(
            return_value=Response(200, json=semantic_response)
        )

        results = list(sync_client.search.semantic_iter("diabetes"))
        assert len(results) == 2

    @respx.mock
    def test_semantic_iter_multiple_pages(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Test semantic_iter auto-pagination."""
        page1_response = {
            "success": True,
            "data": [{"concept_id": 1, "similarity_score": 0.9}],
            "meta": {"pagination": {"page": 1, "has_next": True}},
        }
        page2_response = {
            "success": True,
            "data": [{"concept_id": 2, "similarity_score": 0.8}],
            "meta": {"pagination": {"page": 2, "has_next": False}},
        }

        call_count = 0

        def mock_response(request):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return Response(200, json=page1_response)
            return Response(200, json=page2_response)

        respx.get(f"{base_url}/concepts/semantic-search").mock(side_effect=mock_response)

        results = list(sync_client.search.semantic_iter("diabetes", page_size=1))
        assert len(results) == 2
        assert results[0]["concept_id"] == 1
        assert results[1]["concept_id"] == 2

    @respx.mock
    def test_semantic_iter_empty_response(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Test semantic_iter with empty response yields no items."""
        semantic_response = {
            "success": True,
            "data": [],
            "meta": {"pagination": {"page": 1, "has_next": False}},
        }
        respx.get(f"{base_url}/concepts/semantic-search").mock(
            return_value=Response(200, json=semantic_response)
        )

        results = list(sync_client.search.semantic_iter("nonexistent query"))
        assert len(results) == 0


class TestSimilarSearch:
    """Tests for similar concept search functionality."""

    @respx.mock
    def test_similar_by_concept_id(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test finding similar concepts by concept_id."""
        similar_response = {
            "success": True,
            "data": {
                "similar_concepts": [
                    {
                        "concept_id": 1234,
                        "concept_name": "Similar condition",
                        "domain_id": "Condition",
                        "vocabulary_id": "SNOMED",
                        "concept_class_id": "Clinical Finding",
                        "standard_concept": "S",
                        "concept_code": "12345",
                        "similarity_score": 0.85,
                    }
                ],
                "search_metadata": {
                    "original_query": "4329847",
                    "algorithm_used": "hybrid",
                    "similarity_threshold": 0.7,
                    "total_candidates": 100,
                    "results_returned": 1,
                },
            },
        }
        route = respx.post(f"{base_url}/search/similar").mock(
            return_value=Response(200, json=similar_response)
        )

        result = sync_client.search.similar(concept_id=4329847)
        assert "similar_concepts" in result
        assert len(result["similar_concepts"]) == 1

        # Verify POST body
        import json

        body = json.loads(route.calls[0].request.content)
        assert body["concept_id"] == 4329847
        assert body["algorithm"] == "hybrid"
        assert body["similarity_threshold"] == 0.7

    @respx.mock
    def test_similar_by_concept_name(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Test finding similar concepts by concept_name."""
        route = respx.post(f"{base_url}/search/similar").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "data": {"similar_concepts": [], "search_metadata": {}},
                },
            )
        )

        sync_client.search.similar(concept_name="Type 2 diabetes mellitus")

        import json

        body = json.loads(route.calls[0].request.content)
        assert body["concept_name"] == "Type 2 diabetes mellitus"

    @respx.mock
    def test_similar_by_query(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test finding similar concepts by natural language query."""
        route = respx.post(f"{base_url}/search/similar").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "data": {"similar_concepts": [], "search_metadata": {}},
                },
            )
        )

        sync_client.search.similar(query="high blood sugar condition")

        import json

        body = json.loads(route.calls[0].request.content)
        assert body["query"] == "high blood sugar condition"

    @respx.mock
    def test_similar_with_all_options(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Test similar search with all options."""
        route = respx.post(f"{base_url}/search/similar").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "data": {"similar_concepts": [], "search_metadata": {}},
                },
            )
        )

        sync_client.search.similar(
            concept_id=4329847,
            algorithm="semantic",
            similarity_threshold=0.8,
            page_size=50,
            vocabulary_ids=["SNOMED", "ICD10CM"],
            domain_ids=["Condition"],
            standard_concept="S",
            include_invalid=True,
            include_scores=True,
            include_explanations=True,
        )

        import json

        body = json.loads(route.calls[0].request.content)
        assert body["algorithm"] == "semantic"
        assert body["similarity_threshold"] == 0.8
        assert body["page_size"] == 50
        assert body["vocabulary_ids"] == ["SNOMED", "ICD10CM"]
        assert body["domain_ids"] == ["Condition"]
        assert body["standard_concept"] == "S"
        assert body["include_invalid"] is True
        assert body["include_scores"] is True
        assert body["include_explanations"] is True


class TestAsyncSemanticSearch:
    """Tests for async semantic search functionality."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_semantic_search(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async semantic search."""
        semantic_response = {
            "success": True,
            "data": {
                "results": [{"concept_id": 4329847, "similarity_score": 0.95}],
            },
        }
        respx.get(f"{base_url}/concepts/semantic-search").mock(
            return_value=Response(200, json=semantic_response)
        )

        result = await async_client.search.semantic("heart attack")
        assert "results" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_semantic_with_filters(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async semantic search with filters."""
        route = respx.get(f"{base_url}/concepts/semantic-search").mock(
            return_value=Response(200, json={"success": True, "data": {"results": []}})
        )

        await async_client.search.semantic(
            "diabetes",
            vocabulary_ids=["SNOMED"],
            domain_ids=["Condition"],
            standard_concept="S",
            threshold=0.6,
        )

        url_str = str(route.calls[0].request.url)
        assert "vocabulary_ids=SNOMED" in url_str
        assert "standard_concept=S" in url_str
        assert "threshold=0.6" in url_str

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_semantic_with_all_filters(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async semantic search with all available filters."""
        route = respx.get(f"{base_url}/concepts/semantic-search").mock(
            return_value=Response(200, json={"success": True, "data": {"results": []}})
        )

        await async_client.search.semantic(
            "heart attack",
            vocabulary_ids=["SNOMED", "ICD10CM"],
            domain_ids=["Condition", "Observation"],
            standard_concept="C",
            concept_class_id="Clinical Finding",
            threshold=0.7,
            page=3,
            page_size=50,
        )

        url_str = str(route.calls[0].request.url)
        assert "vocabulary_ids=SNOMED%2CICD10CM" in url_str
        assert "domain_ids=Condition%2CObservation" in url_str
        assert "standard_concept=C" in url_str
        assert "concept_class_id=Clinical+Finding" in url_str
        assert "threshold=0.7" in url_str
        assert "page=3" in url_str
        assert "page_size=50" in url_str

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_semantic_iter_single_page(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async semantic_iter with single page."""
        semantic_response = {
            "success": True,
            "data": [
                {"concept_id": 1, "similarity_score": 0.9},
                {"concept_id": 2, "similarity_score": 0.8},
            ],
            "meta": {"pagination": {"page": 1, "has_next": False}},
        }
        respx.get(f"{base_url}/concepts/semantic-search").mock(
            return_value=Response(200, json=semantic_response)
        )

        results = []
        async for item in async_client.search.semantic_iter("diabetes"):
            results.append(item)

        assert len(results) == 2
        assert results[0]["concept_id"] == 1
        assert results[1]["concept_id"] == 2

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_semantic_iter_multiple_pages(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async semantic_iter auto-pagination across multiple pages."""
        page1_response = {
            "success": True,
            "data": [{"concept_id": 1, "similarity_score": 0.9}],
            "meta": {"pagination": {"page": 1, "has_next": True}},
        }
        page2_response = {
            "success": True,
            "data": [{"concept_id": 2, "similarity_score": 0.8}],
            "meta": {"pagination": {"page": 2, "has_next": True}},
        }
        page3_response = {
            "success": True,
            "data": [{"concept_id": 3, "similarity_score": 0.7}],
            "meta": {"pagination": {"page": 3, "has_next": False}},
        }

        call_count = 0

        def mock_response(request):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return Response(200, json=page1_response)
            elif call_count == 2:
                return Response(200, json=page2_response)
            return Response(200, json=page3_response)

        respx.get(f"{base_url}/concepts/semantic-search").mock(side_effect=mock_response)

        results = []
        async for item in async_client.search.semantic_iter("diabetes", page_size=1):
            results.append(item)

        assert len(results) == 3
        assert results[0]["concept_id"] == 1
        assert results[1]["concept_id"] == 2
        assert results[2]["concept_id"] == 3

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_semantic_iter_with_filters(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async semantic_iter with filters are forwarded correctly."""
        semantic_response = {
            "success": True,
            "data": [{"concept_id": 1, "similarity_score": 0.9}],
            "meta": {"pagination": {"page": 1, "has_next": False}},
        }
        route = respx.get(f"{base_url}/concepts/semantic-search").mock(
            return_value=Response(200, json=semantic_response)
        )

        results = []
        async for item in async_client.search.semantic_iter(
            "diabetes",
            vocabulary_ids=["SNOMED"],
            domain_ids=["Condition"],
            standard_concept="S",
            concept_class_id="Clinical Finding",
            threshold=0.5,
            page_size=10,
        ):
            results.append(item)

        assert len(results) == 1
        url_str = str(route.calls[0].request.url)
        assert "vocabulary_ids=SNOMED" in url_str
        assert "domain_ids=Condition" in url_str
        assert "standard_concept=S" in url_str
        assert "concept_class_id=Clinical+Finding" in url_str
        assert "threshold=0.5" in url_str
        assert "page_size=10" in url_str

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_semantic_iter_empty_response(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async semantic_iter with empty response yields no items."""
        semantic_response = {
            "success": True,
            "data": [],
            "meta": {"pagination": {"page": 1, "has_next": False}},
        }
        respx.get(f"{base_url}/concepts/semantic-search").mock(
            return_value=Response(200, json=semantic_response)
        )

        results = []
        async for item in async_client.search.semantic_iter("nonexistent query"):
            results.append(item)

        assert len(results) == 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_similar(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async similar search."""
        similar_response = {
            "success": True,
            "data": {
                "similar_concepts": [{"concept_id": 1234, "similarity_score": 0.85}],
                "search_metadata": {"algorithm_used": "hybrid"},
            },
        }
        respx.post(f"{base_url}/search/similar").mock(
            return_value=Response(200, json=similar_response)
        )

        result = await async_client.search.similar(concept_id=4329847)
        assert "similar_concepts" in result
        assert len(result["similar_concepts"]) == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_similar_by_concept_name(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async similar search by concept_name."""
        route = respx.post(f"{base_url}/search/similar").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "data": {"similar_concepts": [], "search_metadata": {}},
                },
            )
        )

        await async_client.search.similar(concept_name="Type 2 diabetes mellitus")

        import json

        body = json.loads(route.calls[0].request.content)
        assert body["concept_name"] == "Type 2 diabetes mellitus"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_similar_by_query(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async similar search by natural language query."""
        route = respx.post(f"{base_url}/search/similar").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "data": {"similar_concepts": [], "search_metadata": {}},
                },
            )
        )

        await async_client.search.similar(query="high blood sugar condition")

        import json

        body = json.loads(route.calls[0].request.content)
        assert body["query"] == "high blood sugar condition"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_similar_with_all_options(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async similar search with all options."""
        route = respx.post(f"{base_url}/search/similar").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "data": {"similar_concepts": [], "search_metadata": {}},
                },
            )
        )

        await async_client.search.similar(
            concept_id=4329847,
            algorithm="semantic",
            similarity_threshold=0.8,
            page_size=50,
            vocabulary_ids=["SNOMED", "ICD10CM"],
            domain_ids=["Condition"],
            standard_concept="S",
            include_invalid=True,
            include_scores=True,
            include_explanations=True,
        )

        import json

        body = json.loads(route.calls[0].request.content)
        assert body["algorithm"] == "semantic"
        assert body["similarity_threshold"] == 0.8
        assert body["page_size"] == 50
        assert body["vocabulary_ids"] == ["SNOMED", "ICD10CM"]
        assert body["domain_ids"] == ["Condition"]
        assert body["standard_concept"] == "S"
        assert body["include_invalid"] is True
        assert body["include_scores"] is True
        assert body["include_explanations"] is True
