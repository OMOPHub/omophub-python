"""Integration tests for the relationships resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from omophub import OMOPHub

from tests.conftest import DIABETES_CONCEPT_ID


@pytest.mark.integration
class TestRelationshipsIntegration:
    """Integration tests for relationships resource against production API."""

    def test_get_relationships(self, integration_client: OMOPHub) -> None:
        """Get relationships for a concept."""
        result = integration_client.relationships.get(DIABETES_CONCEPT_ID)

        relationships = result.get("relationships", result)
        assert isinstance(relationships, list)

    def test_get_relationships_with_type_filter(
        self, integration_client: OMOPHub
    ) -> None:
        """Get relationships filtered by type."""
        result = integration_client.relationships.get(
            DIABETES_CONCEPT_ID,
            relationship_ids=["Is a"],
            page_size=50,
        )

        relationships = result.get("relationships", result)
        assert isinstance(relationships, list)

    def test_get_relationships_with_vocabulary_filter(
        self, integration_client: OMOPHub
    ) -> None:
        """Get relationships filtered by target vocabulary."""
        result = integration_client.relationships.get(
            DIABETES_CONCEPT_ID,
            vocabulary_ids=["SNOMED"],
            page_size=100,
        )

        relationships = result.get("relationships", result)
        assert isinstance(relationships, list)

    def test_get_relationship_types(self, integration_client: OMOPHub) -> None:
        """Get available relationship types."""
        result = integration_client.relationships.types()

        types = result.get("relationship_types", result)
        assert isinstance(types, list)
        assert len(types) > 0

    def test_get_relationship_types_with_filters(
        self, integration_client: OMOPHub
    ) -> None:
        """Get relationship types with pagination."""
        result = integration_client.relationships.types(
            page_size=50,
        )

        types = result.get("relationship_types", result)
        assert isinstance(types, list)

    def test_get_relationship_types_basic(self, integration_client: OMOPHub) -> None:
        """Get relationship types with default settings."""
        result = integration_client.relationships.types()

        types = result.get("relationship_types", result)
        assert isinstance(types, list)
