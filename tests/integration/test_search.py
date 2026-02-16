"""Integration tests for the search resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.conftest import extract_data

if TYPE_CHECKING:
    from omophub import OMOPHub


@pytest.mark.integration
class TestSearchIntegration:
    """Integration tests for search resource against production API."""

    def test_basic_search(self, integration_client: OMOPHub) -> None:
        """Search for diabetes concepts."""
        results = integration_client.search.basic("diabetes mellitus", page_size=10)

        concepts = extract_data(results, "concepts")
        assert len(concepts) > 0

    def test_search_with_vocabulary_filter(self, integration_client: OMOPHub) -> None:
        """Search within specific vocabulary."""
        results = integration_client.search.basic(
            "myocardial infarction",
            vocabulary_ids=["SNOMED"],
            page_size=20,
        )

        concepts = extract_data(results, "concepts")
        # If results exist, all should be SNOMED
        for concept in concepts:
            assert concept.get("vocabulary_id") == "SNOMED"

    def test_search_with_domain_filter(self, integration_client: OMOPHub) -> None:
        """Search with domain filter."""
        results = integration_client.search.basic(
            "aspirin",
            domain_ids=["Drug"],
            page_size=10,
        )

        concepts = extract_data(results, "concepts")
        # If results exist, all should be in Drug domain
        for concept in concepts:
            assert concept.get("domain_id") == "Drug"

    def test_search_with_standard_concept_filter(
        self, integration_client: OMOPHub
    ) -> None:
        """Search for standard concepts only."""
        results = integration_client.search.basic(
            "diabetes",
            standard_concept="S",
            page_size=20,
        )

        concepts = extract_data(results, "concepts")
        assert len(concepts) > 0
        # All results should be standard concepts
        for concept in concepts:
            assert concept.get("standard_concept") == "S"

    def test_search_with_multiple_filters_and_pagination(
        self, integration_client: OMOPHub
    ) -> None:
        """Search with multiple filters to test COUNT query parameter binding.

        This test specifically catches COUNT query bugs where parameter binding
        differs between the main query and the count query. If the COUNT query
        fails (like with missing standard_concept parameter), the API would
        return a 500 error instead of results.
        """
        results = integration_client.search.basic(
            "diabetes",
            vocabulary_ids=["SNOMED"],
            domain_ids=["Condition"],
            standard_concept="S",
            page_size=10,
        )

        # Extract concepts - SDK may return list directly or wrapped in dict
        concepts = extract_data(results, "concepts")
        assert len(concepts) > 0, "Expected concepts but got empty result"

        # Verify all filters applied correctly
        for concept in concepts:
            assert concept.get("vocabulary_id") == "SNOMED"
            assert concept.get("domain_id") == "Condition"
            assert concept.get("standard_concept") == "S"

        # Note: The SDK extracts concepts from the response, so we verify
        # the COUNT query worked by the fact that we got results without
        # an error (COUNT query failure would cause HTTP 500)

    def test_autocomplete(self, integration_client: OMOPHub) -> None:
        """Test autocomplete suggestions."""
        result = integration_client.search.autocomplete(
            "diab",
            page_size=10,
        )

        suggestions = extract_data(result, "suggestions")
        assert len(suggestions) > 0
        # Suggestions should start with or contain the query
        for suggestion in suggestions:
            # Handle both flat and nested suggestion structures
            if isinstance(suggestion, dict):
                text = suggestion.get("suggestion", "")
                if isinstance(text, dict):
                    text = text.get("concept_name", "")
                text = str(text).lower()
            else:
                text = str(suggestion).lower()
            assert "diab" in text

    def test_autocomplete_with_filters(self, integration_client: OMOPHub) -> None:
        """Autocomplete with vocabulary and domain filters."""
        result = integration_client.search.autocomplete(
            "hyper",
            vocabulary_ids=["SNOMED"],
            domains=["Condition"],
            page_size=5,
        )

        suggestions = extract_data(result, "suggestions")
        assert isinstance(suggestions, list)

    def test_basic_iter_pagination(self, integration_client: OMOPHub) -> None:
        """Test auto-pagination with basic_iter.

        This test verifies that basic_iter correctly fetches multiple pages
        of results. With page_size=2, we should be able to collect 5 concepts
        which requires fetching at least 3 pages, proving pagination works.
        """
        # Collect concepts using iterator with small page size
        concepts = []
        page_size = 2
        max_concepts = 5

        for concept in integration_client.search.basic_iter(
            "diabetes",
            page_size=page_size,  # Small page size to test pagination
        ):
            concepts.append(concept)
            if len(concepts) >= max_concepts:
                break

        # Should get requested number of concepts (proves pagination worked)
        assert len(concepts) == max_concepts, (
            f"Expected {max_concepts} concepts from paginated iterator, "
            f"got {len(concepts)}. With page_size={page_size}, getting only "
            f"{len(concepts)} concepts suggests pagination is broken."
        )

        # All should have concept_id
        for concept in concepts:
            assert "concept_id" in concept


@pytest.mark.integration
class TestSemanticSearchIntegration:
    """Integration tests for semantic search endpoints."""

    def test_semantic_search_basic(self, integration_client: OMOPHub) -> None:
        """Test basic semantic search returns results with similarity scores."""
        result = integration_client.search.semantic(
            "myocardial infarction", page_size=5
        )

        # SDK may return data wrapped in 'results' key
        results = result.get("results", result)
        if isinstance(results, dict) and "results" in results:
            results = results["results"]

        # Should have results
        assert isinstance(results, list)
        if len(results) > 0:
            # Each result should have similarity score
            for r in results:
                assert "similarity_score" in r or "score" in r
                assert "concept_id" in r

    def test_semantic_search_with_filters(self, integration_client: OMOPHub) -> None:
        """Test semantic search with vocabulary/domain filters."""
        result = integration_client.search.semantic(
            "diabetes",
            vocabulary_ids=["SNOMED"],
            domain_ids=["Condition"],
            threshold=0.5,
            page_size=10,
        )

        results = result.get("results", result)
        if isinstance(results, dict) and "results" in results:
            results = results["results"]

        # If results exist, verify filters applied
        if len(results) > 0:
            for r in results:
                assert r.get("vocabulary_id") == "SNOMED"
                assert r.get("domain_id") == "Condition"

    def test_semantic_search_with_threshold(self, integration_client: OMOPHub) -> None:
        """Test that higher threshold returns fewer or equal results."""
        result_low = integration_client.search.semantic(
            "heart attack", threshold=0.3, page_size=20
        )
        result_high = integration_client.search.semantic(
            "heart attack", threshold=0.8, page_size=20
        )

        results_low = result_low.get("results", [])
        results_high = result_high.get("results", [])

        if isinstance(results_low, dict) and "results" in results_low:
            results_low = results_low["results"]
        if isinstance(results_high, dict) and "results" in results_high:
            results_high = results_high["results"]

        # Guard: skip test if no results to compare
        if not results_low:
            pytest.skip(
                "No results returned for low threshold - cannot test threshold comparison"
            )

        # Higher threshold should return fewer or equal results
        assert len(results_high) <= len(results_low)

    def test_semantic_iter_pagination(self, integration_client: OMOPHub) -> None:
        """Test auto-pagination via semantic_iter."""
        import itertools

        results = list(
            itertools.islice(
                integration_client.search.semantic_iter("diabetes", page_size=5), 10
            )
        )

        # Should get up to 10 results across multiple pages
        assert len(results) > 0
        # Each result should have required fields
        for r in results:
            assert "concept_id" in r

    def test_similar_by_concept_id(self, integration_client: OMOPHub) -> None:
        """Test finding similar concepts by ID."""
        from tests.conftest import MI_CONCEPT_ID

        result = integration_client.search.similar(
            concept_id=MI_CONCEPT_ID, page_size=5
        )

        # Should have similar_concepts key or be a list
        similar = result.get("similar_concepts", result)
        if isinstance(similar, dict) and "similar_concepts" in similar:
            similar = similar["similar_concepts"]

        assert isinstance(similar, list)
        # If results exist, verify structure
        if len(similar) > 0:
            for concept in similar:
                assert "concept_id" in concept

    def test_similar_by_query(self, integration_client: OMOPHub) -> None:
        """Test finding similar concepts by natural language query."""
        result = integration_client.search.similar(
            query="elevated blood glucose", page_size=5
        )

        similar = result.get("similar_concepts", result)
        if isinstance(similar, dict) and "similar_concepts" in similar:
            similar = similar["similar_concepts"]

        assert isinstance(similar, list)

    def test_similar_with_algorithm(self, integration_client: OMOPHub) -> None:
        """Test similar search with different algorithms."""
        from tests.conftest import MI_CONCEPT_ID

        result = integration_client.search.similar(
            concept_id=MI_CONCEPT_ID,
            algorithm="semantic",
            similarity_threshold=0.6,
            page_size=5,
        )

        # Verify response structure
        assert isinstance(result, dict)
        # May have search_metadata with algorithm info
        metadata = result.get("search_metadata", {})
        if metadata:
            assert metadata.get("algorithm_used") in ["semantic", "hybrid", "lexical"]

    def test_similar_with_vocabulary_filter(self, integration_client: OMOPHub) -> None:
        """Test similar search filtered by vocabulary."""
        from tests.conftest import DIABETES_CONCEPT_ID

        result = integration_client.search.similar(
            concept_id=DIABETES_CONCEPT_ID,
            vocabulary_ids=["SNOMED"],
            page_size=10,
        )

        similar = result.get("similar_concepts", [])
        if isinstance(similar, dict) and "similar_concepts" in similar:
            similar = similar["similar_concepts"]

        # If results, all should be from SNOMED
        for concept in similar:
            assert concept.get("vocabulary_id") == "SNOMED"
