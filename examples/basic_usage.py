#!/usr/bin/env python3
"""Basic usage example for the OMOPHub Python SDK."""

import omophub


def main() -> None:
    """Demonstrate basic SDK usage."""
    # Reads OMOPHUB_API_KEY from the environment. To pass it explicitly:
    #   client = omophub.OMOPHub(api_key="oh_your_api_key")
    client = omophub.OMOPHub()

    # Get a concept by ID
    concept = client.concepts.get(201826)
    print(f"Concept: {concept['concept_name']}")
    print(f"  Vocabulary: {concept['vocabulary_id']}")
    print(f"  Code: {concept['concept_code']}")
    print(f"  Domain: {concept['domain_id']}")
    print()

    # Search for concepts - returns a list of concept dicts
    results = client.search.basic(
        "diabetes",
        vocabulary_ids=["SNOMED"],
        page_size=5,
    )
    print("Search results for 'diabetes':")
    for c in results:
        print(f"  {c['concept_id']}: {c['concept_name']}")
    print()

    # List vocabularies - returns a dict with a 'vocabularies' key
    vocabs = client.vocabularies.list(page_size=5)
    print("Available vocabularies:")
    for v in vocabs.get("vocabularies", []):
        print(f"  {v['vocabulary_id']}: {v['vocabulary_name']}")


if __name__ == "__main__":
    main()
