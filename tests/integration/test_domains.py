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

    def test_list_domains_with_stats(self, integration_client: OMOPHub) -> None:
        """List domains with statistics."""
        result = integration_client.domains.list(include_stats=True)

        domains = result.get("domains", [])
        assert len(domains) > 0
        # Verify domains are returned with expected structure including stats
        for domain in domains:
            assert "domain_id" in domain
            assert "concept_count" in domain
            assert "standard_concept_count" in domain

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
