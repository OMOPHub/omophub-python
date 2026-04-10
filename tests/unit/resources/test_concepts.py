"""Tests for the concepts resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import respx
from httpx import Response

if TYPE_CHECKING:
    import omophub
    from omophub import OMOPHub


class TestConceptsResource:
    """Tests for the synchronous concepts resource."""

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
        assert concept["vocabulary_id"] == "SNOMED"

    @respx.mock
    def test_get_concept_with_options(
        self, sync_client: OMOPHub, mock_api_response: dict, base_url: str
    ) -> None:
        """Test getting a concept with include options."""
        route = respx.get(f"{base_url}/concepts/201826").mock(
            return_value=Response(200, json=mock_api_response)
        )

        sync_client.concepts.get(
            201826,
            include_relationships=True,
            include_synonyms=True,
        )

        url_str = str(route.calls[0].request.url)
        assert "include_relationships=true" in url_str
        assert "include_synonyms=true" in url_str

    @respx.mock
    def test_get_concept_by_code(
        self, sync_client: OMOPHub, mock_api_response: dict, base_url: str
    ) -> None:
        """Test getting a concept by vocabulary and code."""
        respx.get(f"{base_url}/concepts/by-code/SNOMED/44054006").mock(
            return_value=Response(200, json=mock_api_response)
        )

        concept = sync_client.concepts.get_by_code("SNOMED", "44054006")
        assert concept["concept_id"] == 201826

    @respx.mock
    def test_batch_concepts(
        self, sync_client: OMOPHub, base_url: str, mock_concept: dict
    ) -> None:
        """Test batch concept retrieval."""
        batch_response = {
            "success": True,
            "data": {
                "concepts": [mock_concept],
                "failed_concepts": [],
                "summary": {"total": 1, "found": 1, "failed": 0},
            },
        }
        respx.post(f"{base_url}/concepts/batch").mock(
            return_value=Response(200, json=batch_response)
        )

        result = sync_client.concepts.batch([201826])
        assert len(result["concepts"]) == 1
        assert result["concepts"][0]["concept_id"] == 201826

    @respx.mock
    def test_batch_concepts_with_options(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Test batch concepts with all options."""
        route = respx.post(f"{base_url}/concepts/batch").mock(
            return_value=Response(200, json={"success": True, "data": {"concepts": []}})
        )

        sync_client.concepts.batch(
            [201826, 1112807],
            include_relationships=True,
            include_synonyms=True,
            include_mappings=True,
            vocabulary_filter=["SNOMED"],
            standard_only=True,
        )

        # Verify POST body was sent
        assert route.calls[0].request.content

    @respx.mock
    def test_suggest_concepts(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test concept suggestions."""
        suggest_response = {
            "success": True,
            "data": [
                {
                    "suggestion": "diabetes mellitus",
                    "type": "concept_name",
                    "match_type": "prefix",
                    "match_score": 0.95,
                },
            ],
        }
        respx.get(f"{base_url}/concepts/suggest").mock(
            return_value=Response(200, json=suggest_response)
        )

        suggestions = sync_client.concepts.suggest("diab")
        assert len(suggestions) == 1
        assert "diabetes" in suggestions[0]["suggestion"]

    @respx.mock
    def test_suggest_concepts_with_filters(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Test suggest with vocabulary and domain filters."""
        route = respx.get(f"{base_url}/concepts/suggest").mock(
            return_value=Response(200, json={"success": True, "data": []})
        )

        sync_client.concepts.suggest(
            "diabetes",
            vocabulary_ids=["SNOMED"],
            domain_ids=["Condition"],
            page_size=20,
        )

        url_str = str(route.calls[0].request.url)
        assert "vocabulary_ids=SNOMED" in url_str
        assert "domain_ids=Condition" in url_str
        assert "page_size=20" in url_str

    @respx.mock
    def test_get_related_concepts(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test getting related concepts."""
        related_response = {
            "success": True,
            "data": {
                "related_concepts": [
                    {"concept_id": 201820, "relatedness_score": 0.85},
                ],
                "analysis": {"total_found": 1},
            },
        }
        respx.get(f"{base_url}/concepts/201826/related").mock(
            return_value=Response(200, json=related_response)
        )

        result = sync_client.concepts.related(201826)
        assert "related_concepts" in result

    @respx.mock
    def test_get_related_with_options(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Test related concepts with all options."""
        route = respx.get(f"{base_url}/concepts/201826/related").mock(
            return_value=Response(
                200, json={"success": True, "data": {"related_concepts": []}}
            )
        )

        sync_client.concepts.related(
            201826,
            relationship_types=["Is a", "Maps to"],
            min_score=0.5,
            page_size=100,
        )

        url_str = str(route.calls[0].request.url)
        assert "relationship_types=Is+a%2CMaps+to" in url_str
        assert "min_score=0.5" in url_str
        assert "page_size=100" in url_str

    @respx.mock
    def test_get_concept_relationships(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Test getting concept relationships."""
        relationships_response = {
            "success": True,
            "data": {
                "relationships": [
                    {"relationship_id": "Is a", "concept_id_2": 201820},
                ],
            },
        }
        respx.get(f"{base_url}/concepts/201826/relationships").mock(
            return_value=Response(200, json=relationships_response)
        )

        result = sync_client.concepts.relationships(201826)
        assert "relationships" in result

    @respx.mock
    def test_get_concept_relationships_with_options(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Test relationships with filter options."""
        route = respx.get(f"{base_url}/concepts/201826/relationships").mock(
            return_value=Response(
                200, json={"success": True, "data": {"relationships": []}}
            )
        )

        sync_client.concepts.relationships(
            201826,
            relationship_ids="Is a",
            vocabulary_ids="SNOMED",
            include_invalid=True,
        )

        url_str = str(route.calls[0].request.url)
        # All params use snake_case to match API standards
        assert "relationship_ids=Is+a" in url_str
        assert "vocabulary_ids=SNOMED" in url_str
        assert "include_invalid=true" in url_str

    @respx.mock
    def test_get_concept_relationships_with_all_options(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Test relationships with all filter options including standard_only and include_reverse."""
        route = respx.get(f"{base_url}/concepts/201826/relationships").mock(
            return_value=Response(
                200, json={"success": True, "data": {"relationships": []}}
            )
        )

        sync_client.concepts.relationships(
            201826,
            relationship_ids=["Is a", "Maps to"],
            vocabulary_ids=["SNOMED", "ICD10CM"],
            domain_ids=["Condition", "Drug"],
            include_invalid=True,
            standard_only=True,
            include_reverse=True,
            vocab_release="2025.1",
        )

        url_str = str(route.calls[0].request.url)
        assert "relationship_ids=Is+a%2CMaps+to" in url_str
        assert "vocabulary_ids=SNOMED%2CICD10CM" in url_str
        assert "domain_ids=Condition%2CDrug" in url_str
        assert "include_invalid=true" in url_str
        assert "standard_only=true" in url_str
        assert "include_reverse=true" in url_str
        assert "vocab_release=2025.1" in url_str

    @respx.mock
    def test_recommended_concepts(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test getting recommended concepts."""
        recommended_response = {
            "success": True,
            "data": {
                "recommendations": [
                    {"concept_id": 201820, "score": 0.95},
                ],
                "meta": {"total": 1},
            },
        }
        respx.post(f"{base_url}/concepts/recommended").mock(
            return_value=Response(200, json=recommended_response)
        )

        result = sync_client.concepts.recommended([201826])
        assert "recommendations" in result

    @respx.mock
    def test_recommended_concepts_with_options(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Test recommended concepts with all options."""
        route = respx.post(f"{base_url}/concepts/recommended").mock(
            return_value=Response(
                200, json={"success": True, "data": {"recommendations": []}}
            )
        )

        sync_client.concepts.recommended(
            [201826, 1112807],
            relationship_types=["Is a", "Maps to"],
            vocabulary_ids=["SNOMED"],
            domain_ids=["Condition"],
            standard_only=False,
            include_invalid=True,
            page=2,
            page_size=50,
        )

        # Verify POST body was sent
        assert route.calls[0].request.content

    @respx.mock
    def test_get_concept_with_hierarchy(
        self, sync_client: OMOPHub, mock_api_response: dict, base_url: str
    ) -> None:
        """Test getting a concept with hierarchy option."""
        route = respx.get(f"{base_url}/concepts/201826").mock(
            return_value=Response(200, json=mock_api_response)
        )

        sync_client.concepts.get(201826, include_hierarchy=True)

        url_str = str(route.calls[0].request.url)
        assert "include_hierarchy=true" in url_str

    @respx.mock
    def test_get_concept_with_vocab_release(
        self, sync_client: OMOPHub, mock_api_response: dict, base_url: str
    ) -> None:
        """Test getting a concept with vocab_release option."""
        route = respx.get(f"{base_url}/concepts/201826").mock(
            return_value=Response(200, json=mock_api_response)
        )

        sync_client.concepts.get(201826, vocab_release="2025.1")

        url_str = str(route.calls[0].request.url)
        assert "vocab_release=2025.1" in url_str

    @respx.mock
    def test_get_by_code_with_all_options(
        self, sync_client: OMOPHub, mock_api_response: dict, base_url: str
    ) -> None:
        """Test getting concept by code with all options."""
        route = respx.get(f"{base_url}/concepts/by-code/SNOMED/44054006").mock(
            return_value=Response(200, json=mock_api_response)
        )

        sync_client.concepts.get_by_code(
            "SNOMED",
            "44054006",
            include_relationships=True,
            include_synonyms=True,
            include_hierarchy=True,
            vocab_release="2025.1",
        )

        url_str = str(route.calls[0].request.url)
        assert "include_relationships=true" in url_str
        assert "include_synonyms=true" in url_str
        assert "include_hierarchy=true" in url_str
        assert "vocab_release=2025.1" in url_str

    @respx.mock
    def test_suggest_concepts_with_vocab_release(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Test suggest with vocab_release option."""
        route = respx.get(f"{base_url}/concepts/suggest").mock(
            return_value=Response(200, json={"success": True, "data": []})
        )

        sync_client.concepts.suggest("diabetes", vocab_release="2025.1")

        url_str = str(route.calls[0].request.url)
        assert "vocab_release=2025.1" in url_str

    @respx.mock
    def test_related_concepts_with_vocab_release(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Test related concepts with vocab_release option."""
        route = respx.get(f"{base_url}/concepts/201826/related").mock(
            return_value=Response(
                200, json={"success": True, "data": {"related_concepts": []}}
            )
        )

        sync_client.concepts.related(201826, vocab_release="2025.1")

        url_str = str(route.calls[0].request.url)
        assert "vocab_release=2025.1" in url_str


class TestAsyncConceptsResource:
    """Tests for the asynchronous concepts resource."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_concept(
        self, async_client: omophub.AsyncOMOPHub, mock_api_response: dict, base_url: str
    ) -> None:
        """Test async getting a concept."""
        respx.get(f"{base_url}/concepts/201826").mock(
            return_value=Response(200, json=mock_api_response)
        )

        concept = await async_client.concepts.get(201826)
        assert concept["concept_id"] == 201826

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_concept_with_options(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async get concept with options."""
        route = respx.get(f"{base_url}/concepts/201826").mock(
            return_value=Response(
                200, json={"success": True, "data": {"concept_id": 201826}}
            )
        )

        await async_client.concepts.get(
            201826,
            include_relationships=True,
            include_synonyms=True,
        )

        url_str = str(route.calls[0].request.url)
        assert "include_relationships=true" in url_str
        assert "include_synonyms=true" in url_str

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_by_code(
        self, async_client: omophub.AsyncOMOPHub, mock_api_response: dict, base_url: str
    ) -> None:
        """Test async get concept by code."""
        respx.get(f"{base_url}/concepts/by-code/SNOMED/44054006").mock(
            return_value=Response(200, json=mock_api_response)
        )

        concept = await async_client.concepts.get_by_code("SNOMED", "44054006")
        assert concept["concept_id"] == 201826

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_batch_concepts(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async batch concepts."""
        batch_response = {
            "success": True,
            "data": {
                "concepts": [{"concept_id": 201826}],
                "summary": {"found": 1},
            },
        }
        respx.post(f"{base_url}/concepts/batch").mock(
            return_value=Response(200, json=batch_response)
        )

        result = await async_client.concepts.batch([201826])
        assert len(result["concepts"]) == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_batch_concepts_with_options(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async batch with options."""
        route = respx.post(f"{base_url}/concepts/batch").mock(
            return_value=Response(200, json={"success": True, "data": {"concepts": []}})
        )

        await async_client.concepts.batch(
            [201826, 1112807, 4329847],
            include_relationships=True,
            include_synonyms=True,
            include_mappings=True,
            vocabulary_filter=["SNOMED", "ICD10CM"],
            standard_only=True,
        )

        assert route.calls[0].request.content

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_suggest(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async suggest."""
        suggest_response = {
            "success": True,
            "data": [{"suggestion": "diabetes"}],
        }
        respx.get(f"{base_url}/concepts/suggest").mock(
            return_value=Response(200, json=suggest_response)
        )

        result = await async_client.concepts.suggest("diab")
        assert len(result) == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_suggest_with_filters(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async suggest with filters."""
        route = respx.get(f"{base_url}/concepts/suggest").mock(
            return_value=Response(200, json={"success": True, "data": []})
        )

        await async_client.concepts.suggest(
            "aspirin",
            vocabulary_ids=["SNOMED"],
            domain_ids=["Drug"],
            page_size=5,
        )

        url_str = str(route.calls[0].request.url)
        assert "vocabulary_ids=SNOMED" in url_str
        assert "domain_ids=Drug" in url_str
        assert "page_size=5" in url_str

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_related(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async get related concepts."""
        respx.get(f"{base_url}/concepts/201826/related").mock(
            return_value=Response(
                200, json={"success": True, "data": {"related_concepts": []}}
            )
        )

        result = await async_client.concepts.related(201826)
        assert "related_concepts" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_related_with_options(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async related with all options."""
        route = respx.get(f"{base_url}/concepts/201826/related").mock(
            return_value=Response(
                200, json={"success": True, "data": {"related_concepts": []}}
            )
        )

        await async_client.concepts.related(
            201826,
            relationship_types=["Is a"],
            min_score=0.7,
            page_size=25,
        )

        url_str = str(route.calls[0].request.url)
        assert "relationship_types=Is+a" in url_str
        assert "min_score=0.7" in url_str
        assert "page_size=25" in url_str

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_relationships(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async get relationships."""
        respx.get(f"{base_url}/concepts/201826/relationships").mock(
            return_value=Response(
                200, json={"success": True, "data": {"relationships": []}}
            )
        )

        result = await async_client.concepts.relationships(201826)
        assert "relationships" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_relationships_with_options(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async relationships with options."""
        route = respx.get(f"{base_url}/concepts/201826/relationships").mock(
            return_value=Response(
                200, json={"success": True, "data": {"relationships": []}}
            )
        )

        await async_client.concepts.relationships(
            201826,
            relationship_ids="Maps to",
            vocabulary_ids="ICD10CM",
            include_invalid=True,
        )

        url_str = str(route.calls[0].request.url)
        assert "relationship_ids=Maps+to" in url_str
        assert "vocabulary_ids=ICD10CM" in url_str
        assert "include_invalid=true" in url_str

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_relationships_with_all_options(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async relationships with all options."""
        route = respx.get(f"{base_url}/concepts/201826/relationships").mock(
            return_value=Response(
                200, json={"success": True, "data": {"relationships": []}}
            )
        )

        await async_client.concepts.relationships(
            201826,
            relationship_ids=["Is a"],
            vocabulary_ids=["SNOMED"],
            domain_ids=["Condition"],
            include_invalid=True,
            standard_only=True,
            include_reverse=True,
            vocab_release="2025.1",
        )

        url_str = str(route.calls[0].request.url)
        assert "domain_ids=Condition" in url_str
        assert "standard_only=true" in url_str
        assert "include_reverse=true" in url_str
        assert "vocab_release=2025.1" in url_str

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_recommended_concepts(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async getting recommended concepts."""
        recommended_response = {
            "success": True,
            "data": {
                "recommendations": [{"concept_id": 201820}],
            },
        }
        respx.post(f"{base_url}/concepts/recommended").mock(
            return_value=Response(200, json=recommended_response)
        )

        result = await async_client.concepts.recommended([201826])
        assert "recommendations" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_recommended_concepts_with_options(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async recommended with all options."""
        route = respx.post(f"{base_url}/concepts/recommended").mock(
            return_value=Response(
                200, json={"success": True, "data": {"recommendations": []}}
            )
        )

        await async_client.concepts.recommended(
            [201826, 1112807],
            relationship_types=["Is a"],
            vocabulary_ids=["SNOMED"],
            domain_ids=["Condition"],
            standard_only=False,
            include_invalid=True,
            page=1,
            page_size=100,
        )

        assert route.calls[0].request.content

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_concept_with_hierarchy(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async get concept with hierarchy option."""
        route = respx.get(f"{base_url}/concepts/201826").mock(
            return_value=Response(
                200, json={"success": True, "data": {"concept_id": 201826}}
            )
        )

        await async_client.concepts.get(201826, include_hierarchy=True)

        url_str = str(route.calls[0].request.url)
        assert "include_hierarchy=true" in url_str

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_concept_with_vocab_release(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async get concept with vocab_release option."""
        route = respx.get(f"{base_url}/concepts/201826").mock(
            return_value=Response(
                200, json={"success": True, "data": {"concept_id": 201826}}
            )
        )

        await async_client.concepts.get(201826, vocab_release="2025.1")

        url_str = str(route.calls[0].request.url)
        assert "vocab_release=2025.1" in url_str

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_by_code_with_all_options(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async get by code with all options."""
        route = respx.get(f"{base_url}/concepts/by-code/SNOMED/44054006").mock(
            return_value=Response(
                200, json={"success": True, "data": {"concept_id": 201826}}
            )
        )

        await async_client.concepts.get_by_code(
            "SNOMED",
            "44054006",
            include_relationships=True,
            include_synonyms=True,
            include_hierarchy=True,
            vocab_release="2025.1",
        )

        url_str = str(route.calls[0].request.url)
        assert "include_relationships=true" in url_str
        assert "include_synonyms=true" in url_str
        assert "include_hierarchy=true" in url_str
        assert "vocab_release=2025.1" in url_str

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_suggest_with_vocab_release(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async suggest with vocab_release option."""
        route = respx.get(f"{base_url}/concepts/suggest").mock(
            return_value=Response(200, json={"success": True, "data": []})
        )

        await async_client.concepts.suggest("diabetes", vocab_release="2025.1")

        url_str = str(route.calls[0].request.url)
        assert "vocab_release=2025.1" in url_str

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_related_with_vocab_release(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async related with vocab_release option."""
        route = respx.get(f"{base_url}/concepts/201826/related").mock(
            return_value=Response(
                200, json={"success": True, "data": {"related_concepts": []}}
            )
        )

        await async_client.concepts.related(201826, vocab_release="2025.1")

        url_str = str(route.calls[0].request.url)
        assert "vocab_release=2025.1" in url_str
