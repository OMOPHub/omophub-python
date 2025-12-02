#!/usr/bin/env python3
"""Examples of searching for concepts using the OMOPHub SDK."""

import omophub

client = omophub.OMOPHub(api_key="oh_your_api_key")


def basic_search() -> None:
    """Demonstrate basic concept search."""
    print("=== Basic Search ===")

    # Simple text search
    results = client.search.basic("heart attack")
    concepts = results.get("concepts", results)
    print(f"Found {len(concepts)} concepts for 'heart attack'")

    for c in concepts[:3]:
        print(f"  {c['concept_id']}: {c['concept_name']} ({c['vocabulary_id']})")


def filtered_search() -> None:
    """Demonstrate search with filters."""
    print("\n=== Filtered Search ===")

    # Search in specific vocabularies
    results = client.search.basic(
        "myocardial infarction",
        vocabulary_ids=["SNOMED", "ICD10CM"],
        domain_ids=["Condition"],
        standard_concept="S",  # Only standard concepts
        page_size=10,
    )
    concepts = results.get("concepts", results)
    print(f"Found {len(concepts)} standard condition concepts")

    for c in concepts[:5]:
        print(f"  [{c['vocabulary_id']}] {c['concept_name']}")


def fuzzy_search() -> None:
    """Demonstrate typo-tolerant fuzzy search."""
    print("\n=== Fuzzy Search ===")

    # Fuzzy search handles typos
    results = client.search.fuzzy("diabetis mellitus")  # Typo in 'diabetes'
    concepts = results.get("concepts", results)
    print("Fuzzy search for 'diabetis mellitus' (typo):")

    for c in concepts[:3]:
        print(f"  {c['concept_name']}")


def autocomplete_example() -> None:
    """Demonstrate autocomplete suggestions."""
    print("\n=== Autocomplete ===")

    # Get suggestions as user types
    suggestions = client.concepts.suggest("hypert", limit=5)

    print("Suggestions for 'hypert':")
    for s in suggestions[:5]:
        print(f"  {s['suggestion']}")


def pagination_example() -> None:
    """Demonstrate pagination through results."""
    print("\n=== Pagination ===")

    # Use iterator for auto-pagination
    count = 0
    for concept in client.search.basic_iter("aspirin", page_size=10):
        count += 1
        if count <= 3:
            print(f"  {concept['concept_name']}")
        if count >= 25:  # Limit for demo
            break

    if count > 3:
        print(f"  ... and {count - 3} more concepts shown (demo limited to {count})")


if __name__ == "__main__":
    basic_search()
    filtered_search()
    fuzzy_search()
    autocomplete_example()
    pagination_example()
