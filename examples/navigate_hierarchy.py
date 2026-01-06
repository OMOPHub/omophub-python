#!/usr/bin/env python3
"""Examples of navigating concept hierarchies using the OMOPHub SDK."""

import omophub

client = omophub.OMOPHub(api_key="oh_your_api_key")


def get_ancestors() -> None:
    """Get ancestors of a concept (parents, grandparents, etc.)."""
    print("=== Concept Ancestors ===")

    # Type 2 diabetes mellitus (SNOMED)
    concept_id = 201826

    # Get ancestors up to 5 levels
    result = client.hierarchy.ancestors(
        concept_id,
        max_levels=5,
        include_distance=True,
    )

    concept = result.get("concept", {})
    ancestors = result.get("ancestors", result)

    print(f"Ancestors of '{concept.get('concept_name', 'Unknown')}':")
    for a in ancestors[:10]:
        level = a.get("level", "?")
        print(f"  Level {level}: {a['concept_name']}")


def get_descendants() -> None:
    """Get descendants of a concept (children, grandchildren, etc.)."""
    print("\n=== Concept Descendants ===")

    # Diabetes mellitus (SNOMED - broader concept)
    concept_id = 201820

    # Get descendants up to 2 levels
    result = client.hierarchy.descendants(
        concept_id,
        max_levels=2,
        include_invalid=False,
    )

    concept = result.get("concept", {})
    descendants = result.get("descendants", result)

    print(f"Descendants of '{concept.get('concept_name', 'Unknown')}':")
    for d in descendants[:10]:
        level = d.get("level", "?")
        print(f"  Level {level}: {d['concept_name']}")


def explore_relationships() -> None:
    """Explore concept relationships."""
    print("\n=== Concept Relationships ===")

    # Aspirin
    concept_id = 1112807

    result = client.concepts.relationships(concept_id, page_size=20)

    relationships = result.get("relationships", result)
    summary = result.get("relationship_summary", {})

    print(f"Relationships for concept {concept_id}:")
    print(f"  Total: {summary.get('total_relationships', len(relationships))}")

    # Group by relationship type
    by_type: dict[str, list] = {}
    for r in relationships:
        rel_id = r.get("relationship_id", "Unknown")
        if rel_id not in by_type:
            by_type[rel_id] = []
        by_type[rel_id].append(r)

    for rel_type, rels in list(by_type.items())[:5]:
        print(f"\n  {rel_type}:")
        for r in rels[:3]:
            target = r.get("target_concept_name", "Unknown")
            print(f"    → {target}")


if __name__ == "__main__":
    get_ancestors()
    get_descendants()
    explore_relationships()
