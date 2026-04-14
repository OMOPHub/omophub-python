"""Integration tests for the FHIR resolver resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from omophub import OMOPHub


@pytest.mark.integration
class TestFhirIntegration:
    """Integration tests for FHIR resolver against the production API."""

    def test_resolve_snomed_live(self, integration_client: OMOPHub) -> None:
        """Resolve SNOMED 44054006 (Type 2 diabetes) to OMOP concept."""
        result = integration_client.fhir.resolve(
            system="http://snomed.info/sct",
            code="44054006",
            resource_type="Condition",
        )

        res = result["resolution"]
        assert res["mapping_type"] == "direct"
        assert res["target_table"] == "condition_occurrence"
        assert res["standard_concept"]["vocabulary_id"] == "SNOMED"
        assert res["standard_concept"]["standard_concept"] == "S"
        assert res["domain_resource_alignment"] == "aligned"

    def test_resolve_icd10cm_live(self, integration_client: OMOPHub) -> None:
        """Resolve ICD-10-CM E11.9 — non-standard, should traverse Maps to."""
        result = integration_client.fhir.resolve(
            system="http://hl7.org/fhir/sid/icd-10-cm",
            code="E11.9",
        )

        res = result["resolution"]
        assert res["vocabulary_id"] == "ICD10CM"
        assert res["source_concept"]["vocabulary_id"] == "ICD10CM"
        assert res["standard_concept"]["standard_concept"] == "S"
        assert res["target_table"] == "condition_occurrence"

    def test_resolve_batch_live(self, integration_client: OMOPHub) -> None:
        """Batch resolve 3 mixed codings."""
        result = integration_client.fhir.resolve_batch(
            [
                {"system": "http://snomed.info/sct", "code": "44054006"},
                {"system": "http://loinc.org", "code": "2339-0"},
                {"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "197696"},
            ]
        )

        assert result["summary"]["total"] == 3
        assert result["summary"]["resolved"] + result["summary"]["failed"] == 3
        assert len(result["results"]) == 3

    def test_resolve_codeable_concept_live(self, integration_client: OMOPHub) -> None:
        """CodeableConcept: SNOMED should win over ICD-10-CM."""
        result = integration_client.fhir.resolve_codeable_concept(
            coding=[
                {"system": "http://snomed.info/sct", "code": "44054006"},
                {"system": "http://hl7.org/fhir/sid/icd-10-cm", "code": "E11.9"},
            ],
            resource_type="Condition",
        )

        assert result["best_match"] is not None
        best = result["best_match"]["resolution"]
        assert best["source_concept"]["vocabulary_id"] == "SNOMED"
        assert best["target_table"] == "condition_occurrence"

    def test_resolve_with_quality_live(self, integration_client: OMOPHub) -> None:
        """Mapping quality signal is returned when requested."""
        result = integration_client.fhir.resolve(
            system="http://snomed.info/sct",
            code="44054006",
            include_quality=True,
        )

        res = result["resolution"]
        assert "mapping_quality" in res
        assert res["mapping_quality"] in ("high", "medium", "low", "manual_review")

    # -- Type interop / duck typing (§B) ---------------------------------

    def test_resolve_with_coding_dict_live(
        self, integration_client: OMOPHub
    ) -> None:
        """``coding=`` kwarg accepts a plain dict against the live API."""
        result = integration_client.fhir.resolve(
            coding={
                "system": "http://snomed.info/sct",
                "code": "44054006",
            },
            resource_type="Condition",
        )
        res = result["resolution"]
        assert res["standard_concept"]["concept_id"] == 201826
        assert res["target_table"] == "condition_occurrence"

    def test_resolve_with_duck_typed_coding_live(
        self, integration_client: OMOPHub
    ) -> None:
        """``coding=`` kwarg accepts a duck-typed object (system/code attrs)."""
        from types import SimpleNamespace

        fake_fhir_coding = SimpleNamespace(
            system="http://snomed.info/sct",
            code="44054006",
            display="Type 2 diabetes mellitus",
        )
        result = integration_client.fhir.resolve(coding=fake_fhir_coding)
        res = result["resolution"]
        assert res["standard_concept"]["concept_id"] == 201826

    def test_resolve_batch_mixed_inputs_live(
        self, integration_client: OMOPHub
    ) -> None:
        """``resolve_batch`` accepts a mixed list of dicts and duck objects."""
        from types import SimpleNamespace

        result = integration_client.fhir.resolve_batch(
            [
                {"system": "http://snomed.info/sct", "code": "44054006"},
                SimpleNamespace(
                    system="http://hl7.org/fhir/sid/icd-10-cm",
                    code="E11.9",
                    display=None,
                ),
            ],
        )
        assert result["summary"]["total"] == 2
        assert result["summary"]["resolved"] >= 1

    def test_resolve_codeable_concept_from_duck_object_live(
        self, integration_client: OMOPHub
    ) -> None:
        """``resolve_codeable_concept`` accepts a CodeableConcept-like object."""
        from types import SimpleNamespace

        cc = SimpleNamespace(
            coding=[
                SimpleNamespace(
                    system="http://snomed.info/sct",
                    code="44054006",
                    display=None,
                ),
                {"system": "http://hl7.org/fhir/sid/icd-10-cm", "code": "E11.9"},
            ],
            text="Type 2 diabetes mellitus",
        )
        result = integration_client.fhir.resolve_codeable_concept(cc)
        assert result["best_match"] is not None
        best = result["best_match"]["resolution"]
        assert best["source_concept"]["vocabulary_id"] == "SNOMED"

    # -- fhir_server_url property (§C) -----------------------------------

    def test_fhir_server_url_property(
        self, integration_client: OMOPHub
    ) -> None:
        """The ``fhir_server_url`` property exposes the R4 endpoint."""
        assert integration_client.fhir_server_url == "https://fhir.omophub.com/fhir/r4"
