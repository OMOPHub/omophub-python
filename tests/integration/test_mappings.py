"""Integration tests for the mappings resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from omophub import OMOPHub

from tests.conftest import DIABETES_CONCEPT_ID, MI_CONCEPT_ID, extract_data


@pytest.mark.integration
class TestMappingsIntegration:
    """Integration tests for mappings resource against production API."""

    def test_get_mappings(self, integration_client: OMOPHub) -> None:
        """Get mappings for a SNOMED concept."""
        result = integration_client.mappings.get(DIABETES_CONCEPT_ID)

        mappings = extract_data(result, "mappings")
        assert isinstance(mappings, list)

    def test_get_mappings_to_icd10(self, integration_client: OMOPHub) -> None:
        """Get ICD-10 mappings for SNOMED concept."""
        result = integration_client.mappings.get(
            DIABETES_CONCEPT_ID,
            target_vocabularies=["ICD10CM"],
            direction="outgoing",
        )

        mappings = extract_data(result, "mappings")
        assert isinstance(mappings, list)

    def test_get_mappings_with_options(self, integration_client: OMOPHub) -> None:
        """Get mappings with quality and context options."""
        result = integration_client.mappings.get(
            DIABETES_CONCEPT_ID,
            include_mapping_quality=True,
            include_context=True,
            page_size=50,
        )

        mappings = extract_data(result, "mappings")
        assert isinstance(mappings, list)

    def test_map_concepts_batch(self, integration_client: OMOPHub) -> None:
        """Map multiple concepts to ICD-10."""
        result = integration_client.mappings.map(
            source_concepts=[DIABETES_CONCEPT_ID, MI_CONCEPT_ID],
            target_vocabulary="ICD10CM",
        )

        # Should get some result structure
        mappings = extract_data(result, "mappings")
        assert isinstance(mappings, list)
