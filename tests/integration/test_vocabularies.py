"""Integration tests for the vocabularies resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.conftest import extract_data

if TYPE_CHECKING:
    from omophub import OMOPHub


@pytest.mark.integration
class TestVocabulariesIntegration:
    """Integration tests for vocabularies resource against production API."""

    def test_list_vocabularies(self, integration_client: OMOPHub) -> None:
        """List all available vocabularies."""
        # Use larger page_size to ensure common vocabularies like SNOMED are included
        result = integration_client.vocabularies.list(page_size=200)

        vocabs = extract_data(result, "vocabularies")
        assert len(vocabs) > 0

        # Check for common vocabularies
        vocab_ids = [v.get("vocabulary_id") for v in vocabs]
        assert "SNOMED" in vocab_ids
        assert "ICD10CM" in vocab_ids

    def test_list_vocabularies_with_stats(self, integration_client: OMOPHub) -> None:
        """List vocabularies with statistics."""
        result = integration_client.vocabularies.list(
            include_stats=True,
            page_size=50,
        )

        vocabs = extract_data(result, "vocabularies")
        assert len(vocabs) > 0
        # Verify vocabularies are returned with expected structure
        assert all("vocabulary_id" in v for v in vocabs)

    def test_get_vocabulary(self, integration_client: OMOPHub) -> None:
        """Get SNOMED vocabulary details."""
        vocab = integration_client.vocabularies.get("SNOMED")

        assert vocab["vocabulary_id"] == "SNOMED"
        assert "vocabulary_name" in vocab

    def test_get_vocabulary_with_options(self, integration_client: OMOPHub) -> None:
        """Get vocabulary with stats and domains."""
        vocab = integration_client.vocabularies.get(
            "SNOMED",
            include_stats=True,
            include_domains=True,
        )

        assert vocab["vocabulary_id"] == "SNOMED"
        assert "vocabulary_name" in vocab

    def test_get_vocabulary_stats(self, integration_client: OMOPHub) -> None:
        """Get SNOMED vocabulary statistics."""
        stats = integration_client.vocabularies.stats("SNOMED")

        assert stats["vocabulary_id"] == "SNOMED"
        # Should have concept counts
        assert (
            "total_concepts" in stats
            or "concept_count" in stats
            or "standard_concepts" in stats
        )

    def test_get_vocabulary_domains(self, integration_client: OMOPHub) -> None:
        """Get vocabulary domains."""
        result = integration_client.vocabularies.domains(vocabulary_ids=["SNOMED"])

        domains = extract_data(result, "domains")
        assert isinstance(domains, list)

    def test_get_vocabulary_concepts(self, integration_client: OMOPHub) -> None:
        """Get concepts in SNOMED vocabulary."""
        result = integration_client.vocabularies.concepts(
            "SNOMED",
            domain_id="Condition",
            standard_only=True,
            page_size=10,
        )

        concepts = extract_data(result, "concepts")
        assert isinstance(concepts, list)
