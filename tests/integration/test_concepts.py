"""Integration tests for the concepts resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from omophub import OMOPHub

from tests.conftest import (
    ASPIRIN_CONCEPT_ID,
    DIABETES_CONCEPT_ID,
    MI_CONCEPT_ID,
    extract_data,
)


@pytest.mark.integration
class TestConceptsIntegration:
    """Integration tests for concepts resource against production API."""

    def test_get_real_concept(self, integration_client: OMOPHub) -> None:
        """Get Type 2 diabetes concept from production API."""
        concept = integration_client.concepts.get(DIABETES_CONCEPT_ID)

        assert concept["concept_id"] == DIABETES_CONCEPT_ID
        assert "Type 2 diabetes" in concept["concept_name"]
        assert concept["vocabulary_id"] == "SNOMED"
        assert concept["domain_id"] == "Condition"
        assert concept["standard_concept"] == "S"

    def test_get_concept_with_synonyms(self, integration_client: OMOPHub) -> None:
        """Get concept with synonyms included."""
        concept = integration_client.concepts.get(
            DIABETES_CONCEPT_ID,
            include_synonyms=True,
        )

        assert concept["concept_id"] == DIABETES_CONCEPT_ID
        # Response structure may vary; check concept exists

    def test_get_concept_by_code(self, integration_client: OMOPHub) -> None:
        """Get concept by SNOMED code."""
        # SNOMED code for Type 2 diabetes mellitus
        concept = integration_client.concepts.get_by_code("SNOMED", "44054006")

        assert concept["concept_id"] == DIABETES_CONCEPT_ID
        assert concept["concept_code"] == "44054006"

    def test_batch_concepts(self, integration_client: OMOPHub) -> None:
        """Batch retrieve multiple concepts."""
        concept_ids = [DIABETES_CONCEPT_ID, ASPIRIN_CONCEPT_ID, MI_CONCEPT_ID]
        result = integration_client.concepts.batch(concept_ids)

        # Check we got results - batch returns concepts array
        concepts = extract_data(result, "concepts")
        assert isinstance(concepts, list)
        assert len(concepts) >= 1, "Batch should return at least one concept"

    def test_suggest_concepts(self, integration_client: OMOPHub) -> None:
        """Get concept suggestions."""
        result = integration_client.concepts.suggest("diabetes", page_size=5)

        # Result is a list of concept objects with concept_name field
        suggestions = extract_data(result, "suggestions")
        assert len(suggestions) > 0
        # Check at least one suggestion contains 'diabetes' in concept_name
        suggestion_texts = []
        for s in suggestions:
            if isinstance(s, dict):
                # Concepts have concept_name, not suggestion
                text = s.get("concept_name", s.get("suggestion", ""))
                suggestion_texts.append(str(text).lower())
            else:
                suggestion_texts.append(str(s).lower())
        assert any("diabetes" in text for text in suggestion_texts)

    def test_suggest_concepts_with_filters(self, integration_client: OMOPHub) -> None:
        """Get concept suggestions with vocabulary filter."""
        result = integration_client.concepts.suggest(
            "aspirin",
            vocabulary_ids=["RxNorm"],
            domain_ids=["Drug"],
            page_size=10,
        )

        # Should get at least one result or empty list
        suggestions = extract_data(result, "suggestions")
        assert isinstance(suggestions, list)

    def test_get_related_concepts(self, integration_client: OMOPHub) -> None:
        """Get related concepts."""
        result = integration_client.concepts.related(
            DIABETES_CONCEPT_ID,
            page_size=10,
        )

        # Should have related_concepts key
        related = extract_data(result, "related_concepts")
        assert isinstance(related, list)

    def test_get_concept_relationships(self, integration_client: OMOPHub) -> None:
        """Get concept relationships."""
        result = integration_client.concepts.relationships(
            DIABETES_CONCEPT_ID,
        )

        # Should have relationships
        relationships = extract_data(result, "relationships")
        assert isinstance(relationships, list)
