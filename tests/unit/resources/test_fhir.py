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
    def test_resolve_codeable_concept_minimal(self, sync_client: OMOPHub, base_url: str) -> None:
        """CodeableConcept with no optional flags (covers False branches)."""
        route = respx.post(f"{base_url}/fhir/resolve/codeable-concept").mock(
            return_value=Response(200, json=CODEABLE_CONCEPT_RESPONSE)
        )

        sync_client.fhir.resolve_codeable_concept(
            coding=[{"system": "http://snomed.info/sct", "code": "44054006"}],
        )

        import json

        body = json.loads(route.calls[0].request.content)
        assert "text" not in body
        assert "resource_type" not in body
        assert "include_recommendations" not in body
        assert "include_quality" not in body

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

    @respx.mock
    @pytest.mark.anyio
    async def test_async_resolve_vocabulary_id_bypass(
        self, async_client: AsyncOMOPHub, base_url: str
    ) -> None:
        """Async resolve with vocabulary_id exercises the bypass branch."""
        route = respx.post(f"{base_url}/fhir/resolve").mock(
            return_value=Response(200, json=ICD10_MAPPED_RESPONSE)
        )

        result = await async_client.fhir.resolve(
            vocabulary_id="ICD10CM",
            code="E11.9",
            include_recommendations=True,
            recommendations_limit=3,
            include_quality=True,
        )

        import json

        body = json.loads(route.calls[0].request.content)
        assert body["vocabulary_id"] == "ICD10CM"
        assert body["include_recommendations"] is True
        assert body["recommendations_limit"] == 3
        assert body["include_quality"] is True
        assert "resolution" in result

    @respx.mock
    @pytest.mark.anyio
    async def test_async_resolve_batch_all_flags(
        self, async_client: AsyncOMOPHub, base_url: str
    ) -> None:
        """Async batch with include_recommendations exercises that branch."""
        route = respx.post(f"{base_url}/fhir/resolve/batch").mock(
            return_value=Response(200, json=BATCH_RESPONSE)
        )

        await async_client.fhir.resolve_batch(
            [{"system": "http://snomed.info/sct", "code": "44054006"}],
            resource_type="Condition",
            include_recommendations=True,
            recommendations_limit=5,
            include_quality=True,
        )

        import json

        body = json.loads(route.calls[0].request.content)
        assert body["include_recommendations"] is True
        assert body["recommendations_limit"] == 5
        assert body["include_quality"] is True

    @respx.mock
    @pytest.mark.anyio
    async def test_async_fhir_property_cached(self, async_client: AsyncOMOPHub, base_url: str) -> None:
        """Accessing client.fhir twice returns the same cached instance."""
        fhir1 = async_client.fhir
        fhir2 = async_client.fhir
        assert fhir1 is fhir2


    @respx.mock
    @pytest.mark.anyio
    async def test_async_resolve_codeable_minimal(
        self, async_client: AsyncOMOPHub, base_url: str
    ) -> None:
        """Async codeable concept with no optional flags (covers False branches)."""
        route = respx.post(f"{base_url}/fhir/resolve/codeable-concept").mock(
            return_value=Response(200, json=CODEABLE_CONCEPT_RESPONSE)
        )

        await async_client.fhir.resolve_codeable_concept(
            coding=[{"system": "http://snomed.info/sct", "code": "44054006"}],
        )

        import json

        body = json.loads(route.calls[0].request.content)
        assert "text" not in body
        assert "resource_type" not in body
        assert "include_recommendations" not in body
        assert "include_quality" not in body

    @respx.mock
    @pytest.mark.anyio
    async def test_async_resolve_batch_minimal(
        self, async_client: AsyncOMOPHub, base_url: str
    ) -> None:
        """Async batch with no optional flags (covers False branches)."""
        route = respx.post(f"{base_url}/fhir/resolve/batch").mock(
            return_value=Response(200, json=BATCH_RESPONSE)
        )

        await async_client.fhir.resolve_batch(
            [{"system": "http://snomed.info/sct", "code": "44054006"}],
        )

        import json

        body = json.loads(route.calls[0].request.content)
        assert "resource_type" not in body
        assert "include_recommendations" not in body
        assert "include_quality" not in body


class TestFhirPropertyCaching:
    """Test lazy-property cache hit on both client types."""

    @respx.mock
    def test_sync_fhir_property_cached(self, sync_client: OMOPHub) -> None:
        """Accessing client.fhir twice returns the same cached instance."""
        fhir1 = sync_client.fhir
        fhir2 = sync_client.fhir
        assert fhir1 is fhir2


# -- Type interop / duck typing ---------------------------------------------


class _DuckCoding:
    """Stand-in for a fhir.resources or fhirpy coding object."""

    def __init__(
        self,
        system: str | None = None,
        code: str | None = None,
        display: str | None = None,
    ) -> None:
        self.system = system
        self.code = code
        self.display = display


class _DuckCodeableConcept:
    """Stand-in for a CodeableConcept-like object."""

    def __init__(self, coding: list[object], text: str | None = None) -> None:
        self.coding = coding
        self.text = text


class TestExtractCodingHelper:
    """Tests for ``_extract_coding`` and ``_coding_to_dict`` normalizers."""

    def test_extract_dict(self) -> None:
        from omophub.resources.fhir import _extract_coding

        assert _extract_coding(
            {"system": "http://snomed.info/sct", "code": "44054006", "display": "T2DM"}
        ) == ("http://snomed.info/sct", "44054006", "T2DM")

    def test_extract_typed_dict(self) -> None:
        from omophub.resources.fhir import _extract_coding

        # Coding is a TypedDict; passing as dict literal exercises the dict branch.
        coding = {"system": "http://loinc.org", "code": "2339-0"}
        assert _extract_coding(coding) == (
            "http://loinc.org",
            "2339-0",
            None,
        )

    def test_extract_duck_object(self) -> None:
        from omophub.resources.fhir import _extract_coding

        obj = _DuckCoding(system="http://snomed.info/sct", code="44054006")
        assert _extract_coding(obj) == (
            "http://snomed.info/sct",
            "44054006",
            None,
        )

    def test_extract_missing_attrs(self) -> None:
        from omophub.resources.fhir import _extract_coding

        class Empty:
            pass

        assert _extract_coding(Empty()) == (None, None, None)

    def test_coding_to_dict_drops_none(self) -> None:
        from omophub.resources.fhir import _coding_to_dict

        obj = _DuckCoding(system="http://snomed.info/sct", code="44054006")
        payload = _coding_to_dict(obj)
        assert payload == {
            "system": "http://snomed.info/sct",
            "code": "44054006",
        }

    def test_coding_to_dict_filters_unknown_keys_from_dict(self) -> None:
        """Dict inputs with FHIR metadata keys must be filtered to the
        resolver's allowed key set - the server should never see
        ``userSelected``, ``extension``, or version markers from
        ``fhir.resources.Coding.model_dump()``.
        """
        from omophub.resources.fhir import _ALLOWED_CODING_KEYS, _coding_to_dict

        model_dump_style = {
            "system": "http://snomed.info/sct",
            "code": "44054006",
            "display": "Type 2 diabetes mellitus",
            "version": "20240301",  # Not in allowed keys
            "userSelected": True,  # FHIR extension
            "extension": [{"url": "http://example.com"}],
            "id": "coding-1",
        }
        payload = _coding_to_dict(model_dump_style)
        assert set(payload.keys()) <= set(_ALLOWED_CODING_KEYS)
        assert payload == {
            "system": "http://snomed.info/sct",
            "code": "44054006",
            "display": "Type 2 diabetes mellitus",
        }

    def test_coding_to_dict_filters_unknown_attrs_from_object(self) -> None:
        """Duck objects with extra attributes are also filtered to the
        allowed key set.
        """
        from types import SimpleNamespace

        from omophub.resources.fhir import _ALLOWED_CODING_KEYS, _coding_to_dict

        obj = SimpleNamespace(
            system="http://snomed.info/sct",
            code="44054006",
            display=None,
            userSelected=True,  # Should not leak into payload
            extension="anything",
        )
        payload = _coding_to_dict(obj)
        assert set(payload.keys()) <= set(_ALLOWED_CODING_KEYS)
        assert payload == {
            "system": "http://snomed.info/sct",
            "code": "44054006",
        }


class TestFhirDuckTyping:
    """Verify resolver methods accept dict, TypedDict, and duck objects."""

    @respx.mock
    def test_resolve_with_coding_dict(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Passing ``coding=`` as a dict produces the same upstream payload."""
        route = respx.post(f"{base_url}/fhir/resolve").mock(
            return_value=Response(200, json=SNOMED_RESOLVE_RESPONSE)
        )
        sync_client.fhir.resolve(
            coding={
                "system": "http://snomed.info/sct",
                "code": "44054006",
            },
        )
        sent = route.calls.last.request.content.decode()
        assert "http://snomed.info/sct" in sent
        assert "44054006" in sent

    @respx.mock
    def test_resolve_with_duck_object(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Passing ``coding=`` as a duck object works via ``getattr``."""
        route = respx.post(f"{base_url}/fhir/resolve").mock(
            return_value=Response(200, json=SNOMED_RESOLVE_RESPONSE)
        )
        sync_client.fhir.resolve(
            coding=_DuckCoding(
                system="http://snomed.info/sct",
                code="44054006",
            ),
        )
        sent = route.calls.last.request.content.decode()
        assert "http://snomed.info/sct" in sent
        assert "44054006" in sent

    @respx.mock
    def test_explicit_kwargs_win_over_coding(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Explicit ``system``/``code`` kwargs override ``coding`` values."""
        route = respx.post(f"{base_url}/fhir/resolve").mock(
            return_value=Response(200, json=SNOMED_RESOLVE_RESPONSE)
        )
        sync_client.fhir.resolve(
            system="http://loinc.org",
            code="2339-0",
            coding=_DuckCoding(
                system="http://snomed.info/sct",
                code="44054006",
            ),
        )
        sent = route.calls.last.request.content.decode()
        assert "http://loinc.org" in sent
        assert "2339-0" in sent
        assert "http://snomed.info/sct" not in sent

    @respx.mock
    def test_resolve_batch_mixed_inputs(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """``resolve_batch`` accepts a mixed list of dicts and duck objects."""
        route = respx.post(f"{base_url}/fhir/resolve/batch").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "data": {
                        "results": [],
                        "summary": {"total": 2, "resolved": 0, "failed": 2},
                    },
                    "meta": {
                        "request_id": "t",
                        "timestamp": "2026-04-10T00:00:00Z",
                        "vocab_release": "2025.2",
                    },
                },
            )
        )
        sync_client.fhir.resolve_batch(
            [
                {"system": "http://snomed.info/sct", "code": "44054006"},
                _DuckCoding(
                    system="http://hl7.org/fhir/sid/icd-10-cm",
                    code="E11.9",
                ),
            ],
        )
        sent = route.calls.last.request.content.decode()
        assert "44054006" in sent
        assert "E11.9" in sent

    @respx.mock
    def test_resolve_codeable_concept_from_duck_object(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """``resolve_codeable_concept`` accepts a full CodeableConcept-like object."""
        route = respx.post(f"{base_url}/fhir/resolve/codeable-concept").mock(
            return_value=Response(200, json=CODEABLE_CONCEPT_RESPONSE)
        )
        cc = _DuckCodeableConcept(
            coding=[
                _DuckCoding(
                    system="http://snomed.info/sct",
                    code="44054006",
                ),
                {"system": "http://hl7.org/fhir/sid/icd-10-cm", "code": "E11.9"},
            ],
            text="Type 2 diabetes mellitus",
        )
        sync_client.fhir.resolve_codeable_concept(cc)
        sent = route.calls.last.request.content.decode()
        assert "44054006" in sent
        assert "E11.9" in sent
        assert "Type 2 diabetes mellitus" in sent

    @respx.mock
    def test_resolve_codeable_concept_from_dict(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """``resolve_codeable_concept`` accepts a dict-shaped CodeableConcept."""
        route = respx.post(f"{base_url}/fhir/resolve/codeable-concept").mock(
            return_value=Response(200, json=CODEABLE_CONCEPT_RESPONSE)
        )
        cc = {
            "coding": [
                {"system": "http://snomed.info/sct", "code": "44054006"},
                {"system": "http://hl7.org/fhir/sid/icd-10-cm", "code": "E11.9"},
            ],
            "text": "Type 2 diabetes mellitus",
        }
        sync_client.fhir.resolve_codeable_concept(cc)
        sent = route.calls.last.request.content.decode()
        assert "44054006" in sent
        assert "E11.9" in sent
        assert "Type 2 diabetes mellitus" in sent

    @respx.mock
    def test_resolve_codeable_concept_from_dict_text_only(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Dict CodeableConcept with no ``coding`` key and no ``text`` is valid.

        Exercises the ``cc_input.get("coding") or []`` fallback and the
        ``cc_input.get("text")`` path when either field is absent.
        """
        route = respx.post(f"{base_url}/fhir/resolve/codeable-concept").mock(
            return_value=Response(200, json=CODEABLE_CONCEPT_RESPONSE)
        )
        # Pass an empty dict - both keys missing; extracted text is None and
        # gets overridden by the explicit ``text=`` kwarg.
        sync_client.fhir.resolve_codeable_concept({}, text="diabetes")
        sent = route.calls.last.request.content.decode()
        assert "diabetes" in sent
        assert '"coding":[]' in sent.replace(" ", "")

    @respx.mock
    def test_resolve_codeable_concept_with_tuple_coding(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """A duck object whose ``.coding`` is a non-list iterable is converted."""
        route = respx.post(f"{base_url}/fhir/resolve/codeable-concept").mock(
            return_value=Response(200, json=CODEABLE_CONCEPT_RESPONSE)
        )
        cc = _DuckCodeableConcept(
            coding=(  # tuple, not a list - exercises the list() conversion
                _DuckCoding(
                    system="http://snomed.info/sct",
                    code="44054006",
                ),
                {"system": "http://hl7.org/fhir/sid/icd-10-cm", "code": "E11.9"},
            ),
            text=None,
        )
        sync_client.fhir.resolve_codeable_concept(cc)
        sent = route.calls.last.request.content.decode()
        assert "44054006" in sent
        assert "E11.9" in sent
