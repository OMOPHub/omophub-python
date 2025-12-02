"""Integration tests for the domains resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from omophub import OMOPHub


@pytest.mark.integration
class TestDomainsIntegration:
    """Integration tests for domains resource against production API."""

    def test_list_domains(self, integration_client: OMOPHub) -> None:
        """List all domains."""
        result = integration_client.domains.list()

        domains = result.get("domains", result)
        assert len(domains) > 0

        # Check for common domains
        domain_ids = [d.get("domain_id") for d in domains]
        assert "Condition" in domain_ids
        assert "Drug" in domain_ids
        assert "Procedure" in domain_ids

    def test_list_domains_with_options(self, integration_client: OMOPHub) -> None:
        """List domains with statistics and examples."""
        result = integration_client.domains.list(
            include_concept_counts=True,
            include_statistics=True,
        )

        domains = result.get("domains", [])
        assert len(domains) > 0
        # Verify domains are returned with expected structure
        assert all("domain_id" in d for d in domains)

    def test_list_domains_with_vocabulary_filter(
        self, integration_client: OMOPHub
    ) -> None:
        """List domains filtered by vocabulary."""
        result = integration_client.domains.list(
            vocabulary_ids=["SNOMED"],
            include_concept_counts=True,
        )

        domains = result.get("domains", [])
        assert isinstance(domains, list)
        assert len(domains) > 0

    def test_get_domain_concepts(self, integration_client: OMOPHub) -> None:
        """Get concepts in Condition domain."""
        result = integration_client.domains.concepts(
            "Condition",
            vocabulary_ids=["SNOMED"],
            standard_only=True,
            page_size=20,
        )

        concepts = result.get("concepts", result)
        assert isinstance(concepts, list)
        # All concepts should be in Condition domain
        for concept in concepts:
            assert concept.get("domain_id") == "Condition"

    def test_get_drug_domain_concepts(self, integration_client: OMOPHub) -> None:
        """Get concepts in Drug domain."""
        result = integration_client.domains.concepts(
            "Drug",
            vocabulary_ids=["RxNorm"],
            standard_only=True,
            page_size=10,
        )

        concepts = result.get("concepts", [])
        assert isinstance(concepts, list)

        # Verify all concepts are in Drug domain
        for concept in concepts:
            assert concept.get("domain_id") == "Drug", "Expected domain_id to be Drug"
