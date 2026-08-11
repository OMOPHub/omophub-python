#!/usr/bin/env python3
"""Examples of mapping concepts between vocabularies using the OMOPHub SDK."""

import omophub


def get_mappings() -> None:
    """Get the mappings defined for a concept."""
    print("=== Concept Mappings ===")

    client = omophub.OMOPHub()

    try:
        # Type 2 diabetes mellitus (SNOMED, standard)
        concept_id = 201826

        # `get()` returns ONE page, and it returns the response's `data` field
        # only -- the `meta.pagination` that would say whether more pages exist
        # is not part of what you get back. See get_every_mapping() below.
        result = client.mappings.get(concept_id)
        mappings = result.get("mappings", [])

        print(f"Mappings for concept {concept_id} (this page: {len(mappings)}):")
        for m in mappings[:10]:
            # A mapping row carries only these fields. Vocabulary id and
            # concept code are NOT part of it -- fetch the target concept if
            # you need them.
            print(
                f"  {m.get('relationship_id')}: "
                f"{m.get('target_concept_id')} {m.get('target_concept_name')}"
            )
    except omophub.OMOPHubError as e:
        print(f"API error: {e.message}")
    finally:
        client.close()


def map_to_a_specific_vocabulary() -> None:
    """Find which ICD-10-CM codes correspond to a SNOMED concept.

    Note the DIRECTION. `Maps to` always points at a *standard* concept, and
    ICD-10-CM is non-standard, so `target_vocabulary="ICD10CM"` on the default
    relationship matches nothing -- it returns an empty list rather than an
    error. The codes that roll up INTO a standard concept are reached with
    `Mapped from`.
    """
    print("\n=== Mapping to a Specific Vocabulary ===")

    client = omophub.OMOPHub()

    try:
        concept_id = 201826

        empty = client.mappings.get(concept_id, target_vocabulary="ICD10CM")
        print(
            f"  'Maps to' + ICD10CM:    {len(empty.get('mappings', []))} rows (as expected)"
        )

        icd_codes = list(
            client.mappings.get_iter(
                concept_id,
                relationship_ids=["Mapped from"],
                target_vocabulary="ICD10CM",
            )
        )
        print(f"  'Mapped from' + ICD10CM: {len(icd_codes)} rows")
        for m in icd_codes[:5]:
            print(f"    <- {m.get('target_concept_id')} {m.get('target_concept_name')}")
    except omophub.OMOPHubError as e:
        print(f"API error: {e.message}")
    finally:
        client.close()


def get_every_mapping() -> None:
    """Walk every page instead of trusting the first one.

    This is the one to copy when building a code list: a partial code list is
    wrong in a way nothing in the result reveals.
    """
    print("\n=== Every Mapping (all pages) ===")

    client = omophub.OMOPHub()

    try:
        concept_id = 201826

        # get_iter() follows has_next to the end; it never has to guess from
        # the page length.
        all_mappings = list(client.mappings.get_iter(concept_id))
        print(f"  {len(all_mappings)} mappings in total")

        # Streaming, if you would rather not hold them all at once.
        for m in client.mappings.get_iter(concept_id):
            _ = m["target_concept_name"]
    except omophub.OMOPHubError as e:
        print(f"API error: {e.message}")
    finally:
        client.close()


def value_as_concept() -> None:
    """Composite concepts decompose across TWO relationships.

    The default returns only the first, so you learn the patient is allergic
    to *a drug* but not *which* drug.
    """
    print("\n=== Value-as-Concept ===")

    client = omophub.OMOPHub()

    try:
        # Allergy to penicillin G
        result = client.mappings.get(
            4167462,
            relationship_ids=["Maps to", "Maps to value"],
        )

        for m in result.get("mappings", []):
            # `Maps to` -> the OMOP concept column;
            # `Maps to value` -> value_as_concept_id.
            column = (
                "value_as_concept_id"
                if m.get("relationship_id") == "Maps to value"
                else "concept_id"
            )
            print(
                f"  {m.get('relationship_id')}: {m.get('target_concept_name')} -> {column}"
            )
    except omophub.OMOPHubError as e:
        print(f"API error: {e.message}")
    finally:
        client.close()


def exclude_invalid() -> None:
    """Deprecated mappings come back by default; pass False to drop them."""
    print("\n=== Valid Mappings Only ===")

    client = omophub.OMOPHub()

    try:
        concept_id = 201826
        with_invalid = list(client.mappings.get_iter(concept_id))
        valid_only = list(client.mappings.get_iter(concept_id, include_invalid=False))

        print(f"  default (includes deprecated): {len(with_invalid)}")
        print(f"  include_invalid=False:         {len(valid_only)}")
    except omophub.OMOPHubError as e:
        print(f"API error: {e.message}")
    finally:
        client.close()


def map_concepts() -> None:
    """Map multiple concepts to a target vocabulary."""
    print("\n=== Batch Concept Mapping ===")

    client = omophub.OMOPHub()

    try:
        # Map SNOMED concepts to ICD-10-CM
        result = client.mappings.map(
            source_concepts=[201826, 4329847],  # Type 2 diabetes, Myocardial infarction
            target_vocabulary="ICD10CM",
        )

        mappings = result.get("mappings", [])
        summary = result.get("mapping_summary", {})

        print(f"Mapped {len(mappings)} concepts to ICD-10-CM")
        print(f"Coverage: {summary.get('coverage_percentage', 'N/A')}%")

        for m in mappings:
            source_name = m.get("source_concept_name", "Unknown")
            target_code = m.get("target_concept_code", "N/A")
            target_name = m.get("target_concept_name", "N/A")
            print(f"\n  {source_name}")
            print(f"    → [{target_code}] {target_name}")
    except omophub.OMOPHubError as e:
        print(f"API error: {e.message}")
    finally:
        client.close()


def lookup_by_code() -> None:
    """Look up a concept by vocabulary code and find its standard mapping."""
    print("\n=== Code Lookup and Mapping ===")

    client = omophub.OMOPHub()

    try:
        # Look up ICD-10-CM code E11 (Type 2 diabetes)
        concept = client.concepts.get_by_code("ICD10CM", "E11")

        print(f"Found: {concept.get('concept_name', 'Unknown')}")
        print(f"  Vocabulary: {concept.get('vocabulary_id', 'Unknown')}")
        print(f"  Standard: {concept.get('standard_concept', 'N/A')}")

        # If it's not a standard concept, find mappings
        if concept.get("standard_concept") != "S":
            mappings = client.mappings.get(concept.get("concept_id", 0))

            print("\n  Mappings to other vocabularies:")
            for m in mappings.get("mappings", [])[:5]:
                print(f"    → {m.get('target_concept_name', 'Unknown')}")
    except omophub.OMOPHubError as e:
        print(f"API error: {e.message}")
    finally:
        client.close()


if __name__ == "__main__":
    get_mappings()
    map_to_a_specific_vocabulary()
    get_every_mapping()
    value_as_concept()
    exclude_invalid()
    map_concepts()
    lookup_by_code()
