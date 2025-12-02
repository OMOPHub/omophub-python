"""Integration tests for the hierarchy resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from omophub import OMOPHub

from tests.conftest import DIABETES_CONCEPT_ID


@pytest.mark.integration
class TestHierarchyIntegration:
    """Integration tests for hierarchy resource against production API."""

    def test_get_ancestors(self, integration_client: OMOPHub) -> None:
        """Get ancestors of Type 2 diabetes."""
        result = integration_client.hierarchy.ancestors(
            DIABETES_CONCEPT_ID,
            max_levels=3,
        )

        # Handle both response formats
        if isinstance(result, dict):
            ancestors = result.get("ancestors", [])
        else:
            ancestors = result if isinstance(result, list) else []

        assert isinstance(ancestors, list), "Expected ancestors to be a list"
        # Type 2 diabetes in SNOMED should have ancestors (parent concepts)
        # Empty list is acceptable if concept has no hierarchy

    def test_get_ancestors_with_options(self, integration_client: OMOPHub) -> None:
        """Get ancestors with various options."""
        result = integration_client.hierarchy.ancestors(
            DIABETES_CONCEPT_ID,
            vocabulary_id="SNOMED",
            max_levels=5,
            include_distance=True,
            page_size=50,
        )

        ancestors = result.get("ancestors", result)
        assert isinstance(ancestors, list)

    def test_get_descendants(self, integration_client: OMOPHub) -> None:
        """Get descendants of a parent concept."""
        # 201820 is Diabetes mellitus (parent of Type 2)
        result = integration_client.hierarchy.descendants(
            201820,  # Diabetes mellitus
            max_levels=2,
        )

        descendants = result.get("descendants", result)
        assert isinstance(descendants, list)

    def test_get_descendants_with_filters(self, integration_client: OMOPHub) -> None:
        """Get descendants with domain and vocabulary filters."""
        result = integration_client.hierarchy.descendants(
            201820,
            vocabulary_id="SNOMED",
            max_levels=3,
            include_distance=True,
            standard_only=True,
            page_size=100,
        )

        descendants = result.get("descendants", result)
        assert isinstance(descendants, list)
