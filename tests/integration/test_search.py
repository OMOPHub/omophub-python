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
