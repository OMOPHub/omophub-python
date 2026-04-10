#!/usr/bin/env python3
"""Examples of FHIR-to-OMOP concept resolution using the OMOPHub SDK.

The FHIR resolver translates FHIR coded values (system URI + code) into
OMOP standard concepts, CDM target tables, and optional Phoebe
recommendations — all in a single API call.

Covers:
  - Direct standard lookups (SNOMED, LOINC, RxNorm)
  - Non-standard code mapping (ICD-10-CM → SNOMED via "Maps to")
  - Text-only semantic search fallback
  - Vocabulary ID bypass (skip URI resolution)
  - Phoebe recommendations and mapping quality signal
  - Batch resolution (up to 100 codings)
  - CodeableConcept resolution with vocabulary preference
  - Async usage
"""

import asyncio

import omophub

# ---------------------------------------------------------------------------
# 1. Direct SNOMED resolution
# ---------------------------------------------------------------------------


def resolve_snomed() -> None:
    """Resolve a SNOMED CT code directly to its OMOP concept."""
    print("=== 1. SNOMED Direct Resolution ===")

    client = omophub.OMOPHub(api_key="oh_your_api_key")
    try:
        result = client.fhir.resolve(
            system="http://snomed.info/sct",
            code="44054006",
            resource_type="Condition",
        )
        res = result["resolution"]
        print(f"  Source: {res['source_concept']['concept_name']}")
        print(f"  Standard: {res['standard_concept']['concept_name']}")
        print(f"  Mapping type: {res['mapping_type']}")  # "direct"
        print(f"  Target table: {res['target_table']}")  # "condition_occurrence"
        print(f"  Alignment: {res['domain_resource_alignment']}")  # "aligned"
    except omophub.OMOPHubError as e:
        print(f"  Error: {e.message}")
    finally:
        client.close()


# ---------------------------------------------------------------------------
# 2. ICD-10-CM mapped to SNOMED via "Maps to"
# ---------------------------------------------------------------------------


def resolve_icd10_mapped() -> None:
    """Resolve a non-standard ICD-10-CM code — automatically traverses Maps to."""
    print("\n=== 2. ICD-10-CM → SNOMED Mapping ===")

    client = omophub.OMOPHub(api_key="oh_your_api_key")
    try:
        result = client.fhir.resolve(
            system="http://hl7.org/fhir/sid/icd-10-cm",
            code="E11.9",
            resource_type="Condition",
        )
        res = result["resolution"]
        print(
            f"  Source: [{res['source_concept']['vocabulary_id']}] {res['source_concept']['concept_name']}"
        )
        print(
            f"  Standard: [{res['standard_concept']['vocabulary_id']}] {res['standard_concept']['concept_name']}"
        )
        print(f"  Mapping type: {res['mapping_type']}")  # "mapped"
        print(f"  Relationship: {res.get('relationship_id', 'N/A')}")  # "Maps to"
        print(f"  Target table: {res['target_table']}")  # "condition_occurrence"
    except omophub.OMOPHubError as e:
        print(f"  Error: {e.message}")
    finally:
        client.close()


# ---------------------------------------------------------------------------
# 3. LOINC direct resolution → measurement table
# ---------------------------------------------------------------------------


def resolve_loinc() -> None:
    """Resolve a LOINC lab code to the OMOP measurement table."""
    print("\n=== 3. LOINC → Measurement ===")

    client = omophub.OMOPHub(api_key="oh_your_api_key")
    try:
        result = client.fhir.resolve(
            system="http://loinc.org",
            code="2339-0",  # Glucose [Mass/volume] in Blood
            resource_type="Observation",
        )
        res = result["resolution"]
        print(f"  Concept: {res['standard_concept']['concept_name']}")
        print(f"  Domain: {res['standard_concept']['domain_id']}")  # "Measurement"
        print(f"  Target table: {res['target_table']}")  # "measurement"
        print(f"  Alignment: {res['domain_resource_alignment']}")  # "aligned"
    except omophub.OMOPHubError as e:
        print(f"  Error: {e.message}")
    finally:
        client.close()


# ---------------------------------------------------------------------------
# 4. RxNorm direct resolution → drug_exposure table
# ---------------------------------------------------------------------------


def resolve_rxnorm() -> None:
    """Resolve an RxNorm drug code to the OMOP drug_exposure table."""
    print("\n=== 4. RxNorm → Drug Exposure ===")

    client = omophub.OMOPHub(api_key="oh_your_api_key")
    try:
        result = client.fhir.resolve(
            system="http://www.nlm.nih.gov/research/umls/rxnorm",
            code="197696",  # Acetaminophen 325 MG Oral Tablet
            resource_type="MedicationRequest",
        )
        res = result["resolution"]
        print(f"  Concept: {res['standard_concept']['concept_name']}")
        print(f"  Target table: {res['target_table']}")  # "drug_exposure"
    except omophub.OMOPHubError as e:
        print(f"  Error: {e.message}")
    finally:
        client.close()


# ---------------------------------------------------------------------------
# 5. Text-only resolution (semantic search fallback)
# ---------------------------------------------------------------------------


def resolve_text_only() -> None:
    """Resolve using only display text — triggers BioLORD semantic search."""
    print("\n=== 5. Text-Only Semantic Fallback ===")

    client = omophub.OMOPHub(api_key="oh_your_api_key")
    try:
        # No system or code — just natural language text
        result = client.fhir.resolve(
            display="Blood Sugar",
            resource_type="Observation",
        )
        res = result["resolution"]
        print(f"  Matched: {res['standard_concept']['concept_name']}")
        print(f"  Mapping type: {res['mapping_type']}")  # "semantic_match"
        print(f"  Similarity: {res.get('similarity_score', 'N/A')}")
        print(f"  Target table: {res['target_table']}")  # "measurement"
    except omophub.OMOPHubError as e:
        print(f"  Error: {e.message}")
    finally:
        client.close()


# ---------------------------------------------------------------------------
# 6. Direct vocabulary_id bypass (skip URI resolution)
# ---------------------------------------------------------------------------


def resolve_vocabulary_id_bypass() -> None:
    """Use vocabulary_id directly when you already know the OMOP vocabulary."""
    print("\n=== 6. Vocabulary ID Bypass ===")

    client = omophub.OMOPHub(api_key="oh_your_api_key")
    try:
        # Skip URI resolution — go straight to the vocabulary
        result = client.fhir.resolve(
            vocabulary_id="ICD10CM",
            code="E11.9",
        )
        res = result["resolution"]
        print(f"  Vocabulary: {res['vocabulary_id']}")  # "ICD10CM"
        print(f"  Standard: {res['standard_concept']['concept_name']}")
    except omophub.OMOPHubError as e:
        print(f"  Error: {e.message}")
    finally:
        client.close()


# ---------------------------------------------------------------------------
# 7. Include Phoebe recommendations
# ---------------------------------------------------------------------------


def resolve_with_recommendations() -> None:
    """Get Phoebe-recommended related concepts alongside the resolution."""
    print("\n=== 7. With Phoebe Recommendations ===")

    client = omophub.OMOPHub(api_key="oh_your_api_key")
    try:
        result = client.fhir.resolve(
            system="http://snomed.info/sct",
            code="44054006",
            include_recommendations=True,
            recommendations_limit=5,
        )
        res = result["resolution"]
        print(f"  Resolved: {res['standard_concept']['concept_name']}")

        recs = res.get("recommendations", [])
        print(f"  Recommendations ({len(recs)}):")
        for rec in recs:
            print(
                f"    - {rec['concept_name']} ({rec['domain_id']}) via {rec['relationship_id']}"
            )
    except omophub.OMOPHubError as e:
        print(f"  Error: {e.message}")
    finally:
        client.close()


# ---------------------------------------------------------------------------
# 8. Include mapping quality signal
# ---------------------------------------------------------------------------


def resolve_with_quality() -> None:
    """Get a mapping quality signal to triage which resolutions need review."""
    print("\n=== 8. With Mapping Quality ===")

    client = omophub.OMOPHub(api_key="oh_your_api_key")
    try:
        # Direct SNOMED match → "high" quality
        result = client.fhir.resolve(
            system="http://snomed.info/sct",
            code="44054006",
            include_quality=True,
        )
        print(
            f"  SNOMED direct → quality: {result['resolution'].get('mapping_quality')}"
        )

        # ICD-10 mapped → quality from validation
        result = client.fhir.resolve(
            system="http://hl7.org/fhir/sid/icd-10-cm",
            code="E11.9",
            include_quality=True,
        )
        print(
            f"  ICD-10 mapped → quality: {result['resolution'].get('mapping_quality')}"
        )

        # Text-only semantic → "medium" quality
        result = client.fhir.resolve(
            display="heart attack",
            resource_type="Condition",
            include_quality=True,
        )
        quality = result["resolution"].get("mapping_quality")
        note = result["resolution"].get("quality_note", "")
        print(f"  Text semantic → quality: {quality}")
        if note:
            print(f"    Note: {note}")
    except omophub.OMOPHubError as e:
        print(f"  Error: {e.message}")
    finally:
        client.close()


# ---------------------------------------------------------------------------
# 9. Batch resolution
# ---------------------------------------------------------------------------


def resolve_batch() -> None:
    """Resolve multiple codings in a single call with per-item error reporting."""
    print("\n=== 9. Batch Resolution ===")

    client = omophub.OMOPHub(api_key="oh_your_api_key")
    try:
        result = client.fhir.resolve_batch(
            [
                {"system": "http://snomed.info/sct", "code": "44054006"},
                {"system": "http://loinc.org", "code": "2339-0"},
                {
                    "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                    "code": "197696",
                },
                {"system": "http://hl7.org/fhir/sid/icd-10-cm", "code": "E11.9"},
                {
                    "system": "http://snomed.info/sct",
                    "code": "99999999-invalid",
                },  # Will fail
            ],
            resource_type="Condition",
            include_quality=True,
        )

        summary = result["summary"]
        print(
            f"  Total: {summary['total']}, Resolved: {summary['resolved']}, Failed: {summary['failed']}"
        )

        for i, item in enumerate(result["results"]):
            if "resolution" in item:
                res = item["resolution"]
                name = res["standard_concept"]["concept_name"]
                table = res["target_table"]
                quality = res.get("mapping_quality", "N/A")
                print(f"  [{i + 1}] {name} → {table} (quality: {quality})")
            else:
                code = item.get("input", {}).get("code", "?")
                error = item["error"]["code"]
                print(f"  [{i + 1}] FAILED code={code}: {error}")
    except omophub.OMOPHubError as e:
        print(f"  Error: {e.message}")
    finally:
        client.close()


# ---------------------------------------------------------------------------
# 10. CodeableConcept resolution (vocabulary preference)
# ---------------------------------------------------------------------------


def resolve_codeable_concept() -> None:
    """Resolve a CodeableConcept with multiple codings — SNOMED wins by preference."""
    print("\n=== 10. CodeableConcept Resolution ===")

    client = omophub.OMOPHub(api_key="oh_your_api_key")
    try:
        result = client.fhir.resolve_codeable_concept(
            coding=[
                {
                    "system": "http://hl7.org/fhir/sid/icd-10-cm",
                    "code": "E11.9",
                    "display": "Type 2 diabetes mellitus without complications",
                },
                {
                    "system": "http://snomed.info/sct",
                    "code": "44054006",
                    "display": "Type 2 diabetes mellitus",
                },
            ],
            resource_type="Condition",
            include_recommendations=True,
            recommendations_limit=3,
        )

        best = result["best_match"]
        if best:
            res = best["resolution"]
            print(
                f"  Best match: [{res['source_concept']['vocabulary_id']}] {res['standard_concept']['concept_name']}"
            )
            print(f"  Target table: {res['target_table']}")

            recs = res.get("recommendations", [])
            if recs:
                print(f"  Recommendations ({len(recs)}):")
                for r in recs:
                    print(f"    - {r['concept_name']}")

        print(f"  Alternatives: {len(result['alternatives'])}")
        for alt in result["alternatives"]:
            alt_res = alt["resolution"]
            print(
                f"    [{alt_res['source_concept']['vocabulary_id']}] {alt_res['standard_concept']['concept_name']}"
            )

        if result["unresolved"]:
            print(f"  Unresolved: {len(result['unresolved'])}")
    except omophub.OMOPHubError as e:
        print(f"  Error: {e.message}")
    finally:
        client.close()


# ---------------------------------------------------------------------------
# 11. CodeableConcept with text fallback
# ---------------------------------------------------------------------------


def resolve_codeable_concept_text_fallback() -> None:
    """When no structured coding resolves, fall back to the text field."""
    print("\n=== 11. CodeableConcept Text Fallback ===")

    client = omophub.OMOPHub(api_key="oh_your_api_key")
    try:
        result = client.fhir.resolve_codeable_concept(
            coding=[
                # This code doesn't exist — will fail
                {"system": "http://loinc.org", "code": "99999-9"},
            ],
            text="Type 2 diabetes mellitus",  # Fallback via semantic search
            resource_type="Condition",
        )

        best = result["best_match"]
        if best:
            res = best["resolution"]
            print(f"  Resolved via: {res['mapping_type']}")  # "semantic_match"
            print(f"  Concept: {res['standard_concept']['concept_name']}")
            print(f"  Similarity: {res.get('similarity_score', 'N/A')}")
        else:
            print("  No resolution found")

        print(f"  Failed codings: {len(result['unresolved'])}")
        for fail in result["unresolved"]:
            print(f"    {fail['error']['code']}: {fail['input'].get('code', '?')}")
    except omophub.OMOPHubError as e:
        print(f"  Error: {e.message}")
    finally:
        client.close()


# ---------------------------------------------------------------------------
# 12. Async usage
# ---------------------------------------------------------------------------


async def async_resolve() -> None:
    """Demonstrate async FHIR resolution with concurrent requests."""
    print("\n=== 12. Async FHIR Resolution ===")

    async with omophub.AsyncOMOPHub(api_key="oh_your_api_key") as client:
        # Single resolve
        result = await client.fhir.resolve(
            system="http://snomed.info/sct",
            code="44054006",
            resource_type="Condition",
        )
        print(f"  Single: {result['resolution']['standard_concept']['concept_name']}")

        # Concurrent: batch + single resolve in parallel
        batch_task = client.fhir.resolve_batch(
            [
                {"system": "http://loinc.org", "code": "2339-0"},
                {
                    "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                    "code": "197696",
                },
            ]
        )
        single_task = client.fhir.resolve(
            system="http://hl7.org/fhir/sid/icd-10-cm",
            code="E11.9",
        )

        batch_result, single_result = await asyncio.gather(batch_task, single_task)

        print(
            f"  Batch: {batch_result['summary']['resolved']}/{batch_result['summary']['total']} resolved"
        )
        print(
            f"  Single: {single_result['resolution']['standard_concept']['concept_name']}"
        )


# ---------------------------------------------------------------------------
# Error handling examples
# ---------------------------------------------------------------------------


def error_handling_examples() -> None:
    """Demonstrate error responses from the FHIR resolver."""
    print("\n=== Error Handling Examples ===")

    client = omophub.OMOPHub(api_key="oh_your_api_key")
    try:
        # Unknown code system URI → 400 with suggestion
        print("  Typo in URI:")
        try:
            client.fhir.resolve(system="http://snomed.info/sc", code="44054006")
        except omophub.OMOPHubError as e:
            print(f"    {e.status_code}: {e.message}")

        # Restricted vocabulary (CPT4) → 403
        print("  CPT4 restricted:")
        try:
            client.fhir.resolve(system="http://www.ama-assn.org/go/cpt", code="99213")
        except omophub.OMOPHubError as e:
            print(f"    {e.status_code}: {e.message}")

        # Code not found → 404
        print("  Non-existent code:")
        try:
            client.fhir.resolve(system="http://snomed.info/sct", code="00000000")
        except omophub.OMOPHubError as e:
            print(f"    {e.status_code}: {e.message}")
    finally:
        client.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    resolve_snomed()
    resolve_icd10_mapped()
    resolve_loinc()
    resolve_rxnorm()
    resolve_text_only()
    resolve_vocabulary_id_bypass()
    resolve_with_recommendations()
    resolve_with_quality()
    resolve_batch()
    resolve_codeable_concept()
    resolve_codeable_concept_text_fallback()
    asyncio.run(async_resolve())
    error_handling_examples()
