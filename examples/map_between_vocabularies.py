#!/usr/bin/env python3
"""Examples of mapping concepts between vocabularies using the OMOPHub SDK."""

import omophub


def get_mappings() -> None:
    """Get mappings for a concept to other vocabularies."""
    print("=== Concept Mappings ===")

    client = omophub.OMOPHub(api_key="oh_your_api_key")

    try:
        # Type 2 diabetes mellitus (SNOMED)
        concept_id = 201826

        result = client.mappings.get(
            concept_id,
            target_vocabularies=["ICD10CM", "Read", "ICD9CM"],
            include_mapping_quality=True,
        )

        source = result.get("source_concept", {})
        mappings = result.get("mappings", [])
        summary = result.get("mapping_summary", {})

        source_name = source.get("concept_name", "Unknown") if source else "Unknown"
        print(f"Mappings for '{source_name}':")
        print(f"  Total mappings: {summary.get('total_mappings', len(mappings))}")

        for m in mappings[:10]:
            target_vocab = m.get("target_vocabulary_id", "?")
            target_code = m.get("target_concept_code", "?")
            target_name = m.get("target_concept_name", "?")
            # Access confidence via quality when available
            quality = m.get("quality", {})
            confidence = quality.get("confidence_score", "N/A") if quality else "N/A"
            print(f"\n  [{target_vocab}] {target_code}")
            print(f"    Name: {target_name}")
            print(f"    Confidence: {confidence}")
    except omophub.OMOPHubError as e:
        print(f"API error: {e.message}")
    finally:
        client.close()


def map_concepts() -> None:
    """Map multiple concepts to a target vocabulary."""
    print("\n=== Batch Concept Mapping ===")

    client = omophub.OMOPHub(api_key="oh_your_api_key")

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

    client = omophub.OMOPHub(api_key="oh_your_api_key")

    try:
        # Look up ICD-10-CM code E11 (Type 2 diabetes)
        concept = client.concepts.get_by_code("ICD10CM", "E11")

        print(f"Found: {concept.get('concept_name', 'Unknown')}")
        print(f"  Vocabulary: {concept.get('vocabulary_id', 'Unknown')}")
        print(f"  Standard: {concept.get('standard_concept', 'N/A')}")

        # If it's not a standard concept, find mappings to standard concepts
        if concept.get("standard_concept") != "S":
            mappings = client.mappings.get(
                concept.get("concept_id", 0),
                standard_only=True,
            )

            print("\n  Standard mappings:")
            for m in mappings.get("mappings", [])[:5]:
                print(f"    → {m.get('target_concept_name', 'Unknown')}")
    except omophub.OMOPHubError as e:
        print(f"API error: {e.message}")
    finally:
        client.close()


if __name__ == "__main__":
    get_mappings()
    map_concepts()
    lookup_by_code()
