#!/usr/bin/env python3
"""Examples of async usage of the OMOPHub SDK."""

import asyncio

import omophub


async def basic_async_usage() -> None:
    """Demonstrate basic async client usage."""
    print("=== Basic Async Usage ===")

    # Use async context manager
    async with omophub.AsyncOMOPHub(api_key="oh_your_api_key") as client:
        # Get a concept
        concept = await client.concepts.get(201826)
        print(f"Concept: {concept['concept_name']}")

        # Search
        results = await client.search.basic("diabetes", page_size=5)
        concepts = results.get("concepts", [])
        print(f"Found {len(concepts)} concepts")


async def concurrent_requests() -> None:
    """Demonstrate concurrent API requests."""
    print("\n=== Concurrent Requests ===")

    async with omophub.AsyncOMOPHub(api_key="oh_your_api_key") as client:
        # Fetch multiple concepts concurrently
        concept_ids = [201826, 4329847, 1112807, 40483312, 37311061]

        tasks = [client.concepts.get(cid) for cid in concept_ids]
        concepts = await asyncio.gather(*tasks)

        print(f"Fetched {len(concepts)} concepts concurrently:")
        for c in concepts:
            print(f"  {c['concept_id']}: {c['concept_name']}")


async def parallel_searches() -> None:
    """Demonstrate parallel search operations."""
    print("\n=== Parallel Searches ===")

    async with omophub.AsyncOMOPHub(api_key="oh_your_api_key") as client:
        # Run multiple searches in parallel
        search_terms = ["diabetes", "hypertension", "asthma", "depression"]

        async def search_and_count(term: str) -> tuple[str, int]:
            results = await client.search.basic(term, page_size=1)
            # Get total from pagination metadata if available
            meta = results.get("meta", {}).get("pagination", {})
            total_items = meta.get("total_items")
            if total_items is not None:
                total = total_items
            else:
                concepts = results.get("concepts", [])
                total = len(concepts) if isinstance(concepts, list) else 0
            return term, total

        tasks = [search_and_count(term) for term in search_terms]
        results = await asyncio.gather(*tasks)

        print("Search results:")
        for term, count in results:
            print(f"  '{term}': {count} concepts")


async def main() -> None:
    """Run all async examples."""
    await basic_async_usage()
    await concurrent_requests()
    await parallel_searches()


if __name__ == "__main__":
    asyncio.run(main())
