"""Tests for the FHIR resolver resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import respx
from httpx import Response

if TYPE_CHECKING:
    from omophub import AsyncOMOPHub, OMOPHub


# -- Fixtures ----------------------------------------------------------------

SNOMED_RESOLVE_RESPONSE = {
    "success": True,
    "data": {
        "input": {
            "system": "http://snomed.info/sct",
            "code": "44054006",
            "resource_type": "Condition",
        },
        "resolution": {
            "vocabulary_id": "SNOMED",
            "source_concept": {
                "concept_id": 201826,
                "concept_name": "Type 2 diabetes mellitus",
                "concept_code": "44054006",
                "vocabulary_id": "SNOMED",
                "domain_id": "Condition",
                "concept_class_id": "Clinical Finding",
                "standard_concept": "S",
            },
            "standard_concept": {
                "concept_id": 201826,
                "concept_name": "Type 2 diabetes mellitus",
                "concept_code": "44054006",
                "vocabulary_id": "SNOMED",
                "domain_id": "Condition",
                "concept_class_id": "Clinical Finding",
                "standard_concept": "S",
            },
            "mapping_type": "direct",
            "target_table": "condition_occurrence",
            "domain_resource_alignment": "aligned",
        },
    },
    "meta": {"request_id": "test", "timestamp": "2026-04-10T00:00:00Z", "vocab_release": "2025.2"},
}

ICD10_MAPPED_RESPONSE = {
    "success": True,
    "data": {
        "input": {"system": "http://hl7.org/fhir/sid/icd-10-cm", "code": "E11.9"},
        "resolution": {
            "vocabulary_id": "ICD10CM",
            "source_concept": {
                "concept_id": 45576876,
                "concept_name": "Type 2 diabetes mellitus without complications",
                "concept_code": "E11.9",
                "vocabulary_id": "ICD10CM",
                "domain_id": "Condition",
                "concept_class_id": "5-char billing code",
                "standard_concept": None,
            },
            "standard_concept": {
                "concept_id": 201826,
                "concept_name": "Type 2 diabetes mellitus",
                "concept_code": "44054006",
                "vocabulary_id": "SNOMED",
                "domain_id": "Condition",
                "concept_class_id": "Clinical Finding",
                "standard_concept": "S",
            },
            "mapping_type": "mapped",
            "relationship_id": "Maps to",
            "target_table": "condition_occurrence",
            "domain_resource_alignment": "not_checked",
            "mapping_quality": "high",
        },
    },
}

BATCH_RESPONSE = {
    "success": True,
    "data": {
        "results": [SNOMED_RESOLVE_RESPONSE["data"]],
        "summary": {"total": 1, "resolved": 1, "failed": 0},
    },
}

CODEABLE_CONCEPT_RESPONSE = {
    "success": True,
    "data": {
        "input": {
            "coding": [
                {"system": "http://snomed.info/sct", "code": "44054006"},
                {"system": "http://hl7.org/fhir/sid/icd-10-cm", "code": "E11.9"},
            ],
            "resource_type": "Condition",
        },
        "best_match": SNOMED_RESOLVE_RESPONSE["data"],
        "alternatives": [ICD10_MAPPED_RESPONSE["data"]],
        "unresolved": [],
    },
}


# -- Sync tests --------------------------------------------------------------


class TestFhirSync:
    """Tests for the synchronous Fhir resource."""

    @respx.mock
    def test_resolve_snomed_direct(self, sync_client: OMOPHub, base_url: str) -> None:
        """SNOMED direct resolution returns correct shape."""
        respx.post(f"{base_url}/fhir/resolve").mock(
            return_value=Response(200, json=SNOMED_RESOLVE_RESPONSE)
        )

        result = sync_client.fhir.resolve(
            system="http://snomed.info/sct",
            code="44054006",
            resource_type="Condition",
        )

        assert result["resolution"]["mapping_type"] == "direct"
        assert result["resolution"]["target_table"] == "condition_occurrence"
        assert result["resolution"]["standard_concept"]["concept_id"] == 201826

    @respx.mock
    def test_resolve_icd10_mapped(self, sync_client: OMOPHub, base_url: str) -> None:
        """ICD-10-CM maps to a standard SNOMED concept."""
        respx.post(f"{base_url}/fhir/resolve").mock(
            return_value=Response(200, json=ICD10_MAPPED_RESPONSE)
        )

        result = sync_client.fhir.resolve(
            system="http://hl7.org/fhir/sid/icd-10-cm",
            code="E11.9",
            include_quality=True,
        )

        assert result["resolution"]["mapping_type"] == "mapped"
        assert result["resolution"]["relationship_id"] == "Maps to"
        assert result["resolution"]["mapping_quality"] == "high"

    @respx.mock
    def test_resolve_text_only(self, sync_client: OMOPHub, base_url: str) -> None:
        """Display-only input triggers semantic search fallback."""
        semantic_response = {
            "success": True,
            "data": {
                "input": {"display": "Blood Sugar", "resource_type": "Observation"},
                "resolution": {
                    "vocabulary_id": None,
                    "source_concept": {
                        "concept_id": 3004501,
                        "concept_name": "Glucose [Mass/volume] in Blood",
                        "concept_code": "2339-0",
                        "vocabulary_id": "LOINC",
                        "domain_id": "Measurement",
                        "concept_class_id": "Lab Test",
                        "standard_concept": "S",
                    },
                    "standard_concept": {
                        "concept_id": 3004501,
                        "concept_name": "Glucose [Mass/volume] in Blood",
                        "concept_code": "2339-0",
                        "vocabulary_id": "LOINC",
                        "domain_id": "Measurement",
                        "concept_class_id": "Lab Test",
                        "standard_concept": "S",
                    },
                    "mapping_type": "semantic_match",
                    "similarity_score": 0.91,
                    "target_table": "measurement",
                    "domain_resource_alignment": "aligned",
                },
            },
        }
        respx.post(f"{base_url}/fhir/resolve").mock(
            return_value=Response(200, json=semantic_response)
        )

        result = sync_client.fhir.resolve(display="Blood Sugar", resource_type="Observation")

        assert result["resolution"]["mapping_type"] == "semantic_match"
        assert result["resolution"]["similarity_score"] == 0.91

    @respx.mock
    def test_resolve_with_recommendations(self, sync_client: OMOPHub, base_url: str) -> None:
        """Recommendations are included when requested."""
        recs_response = {**SNOMED_RESOLVE_RESPONSE}
        recs_response["data"] = {
            **SNOMED_RESOLVE_RESPONSE["data"],
            "resolution": {
                **SNOMED_RESOLVE_RESPONSE["data"]["resolution"],
                "recommendations": [
                    {
                        "concept_id": 4193704,
                        "concept_name": "Hyperglycemia",
                        "vocabulary_id": "SNOMED",
                        "domain_id": "Condition",
                        "concept_class_id": "Clinical Finding",
                        "standard_concept": "S",
                        "relationship_id": "Has finding",
                    }
                ],
            },
        }
        route = respx.post(f"{base_url}/fhir/resolve").mock(
            return_value=Response(200, json=recs_response)
        )

        result = sync_client.fhir.resolve(
            system="http://snomed.info/sct",
            code="44054006",
            include_recommendations=True,
            recommendations_limit=3,
        )

        assert len(result["resolution"]["recommendations"]) == 1
        # Verify the request body included the flags
        import json

        body = json.loads(route.calls[0].request.content)
        assert body["include_recommendations"] is True
        assert body["recommendations_limit"] == 3

    @respx.mock
    def test_resolve_unknown_system_400(self, sync_client: OMOPHub, base_url: str) -> None:
        """Unknown URI raises an API error."""
        respx.post(f"{base_url}/fhir/resolve").mock(
            return_value=Response(
                400,
                json={
                    "success": False,
                    "error": {
                        "code": "unknown_system",
                        "message": "Unknown FHIR code system URI",
                        "details": {"suggestion": "http://snomed.info/sct"},
                    },
                },
            )
        )

        with pytest.raises(Exception):
            sync_client.fhir.resolve(system="http://snomed.info/sc", code="44054006")

    @respx.mock
    def test_resolve_cpt4_403(self, sync_client: OMOPHub, base_url: str) -> None:
        """CPT4 raises a 403 restricted error."""
        respx.post(f"{base_url}/fhir/resolve").mock(
            return_value=Response(
                403,
                json={
                    "success": False,
                    "error": {
                        "code": "vocabulary_restricted",
                        "message": "CPT4 is excluded",
                    },
                },
            )
        )

        with pytest.raises(Exception):
            sync_client.fhir.resolve(system="http://www.ama-assn.org/go/cpt", code="99213")

    @respx.mock
    def test_resolve_batch(self, sync_client: OMOPHub, base_url: str) -> None:
        """Batch resolution returns results and summary."""
        respx.post(f"{base_url}/fhir/resolve/batch").mock(
            return_value=Response(200, json=BATCH_RESPONSE)
        )

        result = sync_client.fhir.resolve_batch(
            [{"system": "http://snomed.info/sct", "code": "44054006"}]
        )

        assert result["summary"]["total"] == 1
        assert result["summary"]["resolved"] == 1
        assert len(result["results"]) == 1

    @respx.mock
    def test_resolve_codeable_concept(self, sync_client: OMOPHub, base_url: str) -> None:
        """CodeableConcept resolution returns best_match and alternatives."""
        respx.post(f"{base_url}/fhir/resolve/codeable-concept").mock(
            return_value=Response(200, json=CODEABLE_CONCEPT_RESPONSE)
        )

        result = sync_client.fhir.resolve_codeable_concept(
            coding=[
                {"system": "http://snomed.info/sct", "code": "44054006"},
                {"system": "http://hl7.org/fhir/sid/icd-10-cm", "code": "E11.9"},
            ],
            resource_type="Condition",
        )

        assert result["best_match"] is not None
        assert result["best_match"]["resolution"]["source_concept"]["vocabulary_id"] == "SNOMED"
        assert len(result["alternatives"]) == 1

    @respx.mock
    def test_resolve_batch_with_all_options(self, sync_client: OMOPHub, base_url: str) -> None:
        """Batch passes resource_type, include_recommendations, and include_quality."""
        route = respx.post(f"{base_url}/fhir/resolve/batch").mock(
            return_value=Response(200, json=BATCH_RESPONSE)
        )

        sync_client.fhir.resolve_batch(
            [{"system": "http://snomed.info/sct", "code": "44054006"}],
            resource_type="Condition",
            include_recommendations=True,
            recommendations_limit=3,
            include_quality=True,
        )

        import json

        body = json.loads(route.calls[0].request.content)
        assert body["resource_type"] == "Condition"
        assert body["include_recommendations"] is True
        assert body["recommendations_limit"] == 3
        assert body["include_quality"] is True

    @respx.mock
    def test_resolve_codeable_concept_with_all_options(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """CodeableConcept passes text, resource_type, and enrichment flags."""
        route = respx.post(f"{base_url}/fhir/resolve/codeable-concept").mock(
            return_value=Response(200, json=CODEABLE_CONCEPT_RESPONSE)
        )

        sync_client.fhir.resolve_codeable_concept(
            coding=[{"system": "http://snomed.info/sct", "code": "44054006"}],
            text="Type 2 diabetes",
            resource_type="Condition",
            include_recommendations=True,
            recommendations_limit=5,
            include_quality=True,
        )

        import json

        body = json.loads(route.calls[0].request.content)
        assert body["text"] == "Type 2 diabetes"
        assert body["resource_type"] == "Condition"
        assert body["include_recommendations"] is True
        assert body["include_quality"] is True

    @respx.mock
    def test_resolve_sends_correct_body(self, sync_client: OMOPHub, base_url: str) -> None:
        """Verify the POST body includes only non-None parameters."""
        route = respx.post(f"{base_url}/fhir/resolve").mock(
            return_value=Response(200, json=SNOMED_RESOLVE_RESPONSE)
        )

        sync_client.fhir.resolve(
            system="http://snomed.info/sct",
            code="44054006",
            resource_type="Condition",
        )

        import json

        body = json.loads(route.calls[0].request.content)
        assert body == {
            "system": "http://snomed.info/sct",
            "code": "44054006",
            "resource_type": "Condition",
        }
        # Ensure optional flags are NOT sent when they're default False
        assert "include_recommendations" not in body
        assert "include_quality" not in body


# -- Async tests -------------------------------------------------------------


class TestFhirAsync:
    """Tests for the asynchronous AsyncFhir resource."""

    @respx.mock
    @pytest.mark.anyio
    async def test_async_resolve(self, async_client: AsyncOMOPHub, base_url: str) -> None:
        """Async resolve returns the same shape as sync."""
        respx.post(f"{base_url}/fhir/resolve").mock(
            return_value=Response(200, json=SNOMED_RESOLVE_RESPONSE)
        )

        result = await async_client.fhir.resolve(
            system="http://snomed.info/sct",
            code="44054006",
        )

        assert result["resolution"]["mapping_type"] == "direct"
        assert result["resolution"]["target_table"] == "condition_occurrence"

    @respx.mock
    @pytest.mark.anyio
    async def test_async_resolve_batch(self, async_client: AsyncOMOPHub, base_url: str) -> None:
        """Async batch resolve returns results and summary."""
        respx.post(f"{base_url}/fhir/resolve/batch").mock(
            return_value=Response(200, json=BATCH_RESPONSE)
        )

        result = await async_client.fhir.resolve_batch(
            [{"system": "http://snomed.info/sct", "code": "44054006"}],
            resource_type="Condition",
            include_quality=True,
        )

        assert result["summary"]["total"] == 1

    @respx.mock
    @pytest.mark.anyio
    async def test_async_resolve_codeable_concept(
        self, async_client: AsyncOMOPHub, base_url: str
    ) -> None:
        """Async codeable concept resolve returns best_match."""
        respx.post(f"{base_url}/fhir/resolve/codeable-concept").mock(
            return_value=Response(200, json=CODEABLE_CONCEPT_RESPONSE)
        )

        result = await async_client.fhir.resolve_codeable_concept(
            coding=[
                {"system": "http://snomed.info/sct", "code": "44054006"},
                {"system": "http://hl7.org/fhir/sid/icd-10-cm", "code": "E11.9"},
            ],
            text="Type 2 diabetes",
            resource_type="Condition",
            include_recommendations=True,
            include_quality=True,
        )

        assert result["best_match"] is not None
