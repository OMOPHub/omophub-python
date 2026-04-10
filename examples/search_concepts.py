#!/usr/bin/env python3
"""Examples of searching for concepts using the OMOPHub SDK.

Demonstrates: basic search, filtered search, autocomplete, pagination,
semantic search, similarity search, bulk lexical search, and bulk semantic search.
"""

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


def bulk_lexical_search() -> None:
    """Demonstrate bulk lexical search — multiple queries in one call."""
    print("\n=== Bulk Lexical Search ===")

    # Search for multiple terms at once (up to 50)
    results = client.search.bulk_basic(
        [
            {"search_id": "q1", "query": "diabetes mellitus"},
            {"search_id": "q2", "query": "hypertension"},
            {"search_id": "q3", "query": "aspirin"},
        ],
        defaults={"vocabulary_ids": ["SNOMED"], "page_size": 5},
    )

    for item in results["results"]:
        print(f"  {item['search_id']}: {len(item['results'])} results ({item['status']})")

    # Per-query overrides — different domains per query
    results = client.search.bulk_basic(
        [
            {"search_id": "conditions", "query": "diabetes", "domain_ids": ["Condition"]},
            {"search_id": "drugs", "query": "metformin", "domain_ids": ["Drug"]},
        ],
        defaults={"vocabulary_ids": ["SNOMED", "RxNorm"], "page_size": 3},
    )

    print("\n  Per-query domain overrides:")
    for item in results["results"]:
        print(f"    {item['search_id']}:")
        for c in item["results"]:
            print(f"      {c['concept_name']} ({c['vocabulary_id']}/{c['domain_id']})")


def bulk_semantic_search() -> None:
    """Demonstrate bulk semantic search — multiple NLP queries in one call."""
    print("\n=== Bulk Semantic Search ===")

    # Search for multiple natural-language queries (up to 25)
    results = client.search.bulk_semantic(
        [
            {"search_id": "s1", "query": "heart failure treatment options"},
            {"search_id": "s2", "query": "type 2 diabetes medication"},
            {"search_id": "s3", "query": "elevated blood pressure"},
        ],
        defaults={"threshold": 0.5, "page_size": 5},
    )

    for item in results["results"]:
        count = item.get("result_count", len(item["results"]))
        print(f"  {item['search_id']}: {count} results ({item['status']})")

        # Show top result per query
        if item["results"]:
            top = item["results"][0]
            print(f"    Top: {top['concept_name']} (score: {top['similarity_score']:.2f})")


def autocomplete_example() -> None:
    """Demonstrate autocomplete suggestions."""
    print("\n=== Autocomplete ===")

    # Get suggestions as user types
    suggestions = client.concepts.suggest("hypert", page_size=5)

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


def semantic_search() -> None:
    """Demonstrate semantic search using neural embeddings."""
    print("\n=== Semantic Search ===")

    # Natural language search - understands clinical intent
    results = client.search.semantic("high blood sugar levels")
    for r in results["results"][:3]:
        print(f"  {r['concept_name']} (similarity: {r['similarity_score']:.2f})")

    # Filtered semantic search with minimum threshold
    results = client.search.semantic(
        "heart attack",
        vocabulary_ids=["SNOMED"],
        domain_ids=["Condition"],
        threshold=0.5,
    )
    print(f"  Found {len(results['results'])} SNOMED conditions for 'heart attack'")


def semantic_pagination() -> None:
    """Demonstrate auto-pagination with semantic_iter."""
    print("\n=== Semantic Pagination ===")

    count = 0
    for result in client.search.semantic_iter("chronic kidney disease", page_size=20):
        count += 1
        if count <= 3:
            print(f"  {result['concept_id']}: {result['concept_name']}")
        if count >= 50:  # Limit for demo
            break

    if count > 3:
        print(f"  ... and {count - 3} more results (demo limited to {count})")


def similarity_search() -> None:
    """Demonstrate similarity search."""
    print("\n=== Similarity Search ===")

    # Find concepts similar to Type 2 diabetes mellitus (concept_id=201826)
    results = client.search.similar(concept_id=201826, algorithm="hybrid")
    print("Concepts similar to 'Type 2 diabetes mellitus':")
    for r in results["results"][:5]:
        print(f"  {r['concept_name']} (score: {r['similarity_score']:.2f})")

    # Find similar using a natural language query with semantic algorithm
    results = client.search.similar(
        query="medications for high blood pressure",
        algorithm="semantic",
        similarity_threshold=0.6,
        vocabulary_ids=["RxNorm"],
        include_scores=True,
    )
    print(f"\n  Found {len(results['results'])} similar RxNorm concepts")


if __name__ == "__main__":
    basic_search()
    filtered_search()
    autocomplete_example()
    pagination_example()
    semantic_search()
    semantic_pagination()
    similarity_search()
    bulk_lexical_search()
    bulk_semantic_search()
