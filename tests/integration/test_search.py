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

    def test_autocomplete(self, integration_client: OMOPHub) -> None:
        """Test autocomplete suggestions."""
        result = integration_client.search.autocomplete(
            "diab",
            max_suggestions=10,
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
            max_suggestions=5,
        )

        suggestions = extract_data(result, "suggestions")
        assert isinstance(suggestions, list)

    def test_basic_iter_pagination(self, integration_client: OMOPHub) -> None:
        """Test auto-pagination with basic_iter."""
        # Collect first 5 concepts using iterator
        concepts = []
        for concept in integration_client.search.basic_iter(
            "diabetes",
            page_size=2,  # Small page size to test pagination
        ):
            concepts.append(concept)
            if len(concepts) >= 5:
                break

        assert len(concepts) == 5
        # All should have concept_id
        for concept in concepts:
            assert "concept_id" in concept
