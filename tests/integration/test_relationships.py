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
            relationship_type="Is a",
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
            target_vocabulary="SNOMED",
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
        """Get relationship types with filters."""
        result = integration_client.relationships.types(
            vocabulary_ids=["SNOMED"],
            include_reverse=True,
            include_usage_stats=True,
            page_size=50,
        )

        types = result.get("relationship_types", result)
        assert isinstance(types, list)

    def test_get_relationship_types_by_category(
        self, integration_client: OMOPHub
    ) -> None:
        """Get relationship types by category."""
        result = integration_client.relationships.types(
            category="hierarchy",
            standard_only=True,
        )

        types = result.get("relationship_types", result)
        assert isinstance(types, list)
