#!/usr/bin/env python3
"""Examples of async usage of the OMOPHub SDK."""

import asyncio

import omophub


async def basic_async_usage() -> None:
    """Demonstrate basic async client usage."""
    print("=== Basic Async Usage ===")

    # Use async context manager
    async with omophub.AsyncOMOPHub() as client:
        # Get a concept
        concept = await client.concepts.get(201826)
        print(f"Concept: {concept['concept_name']}")

        # Search - returns a flat list of concept dicts
        concepts = await client.search.basic("diabetes", page_size=5)
        print(f"Found {len(concepts)} concepts")


async def concurrent_requests() -> None:
    """Demonstrate concurrent API requests."""
    print("\n=== Concurrent Requests ===")

    async with omophub.AsyncOMOPHub() as client:
        # Fetch multiple concepts concurrently
        concept_ids = [201826, 4329847, 1112807, 316866, 37311061]

        tasks = [client.concepts.get(cid) for cid in concept_ids]
        concepts = await asyncio.gather(*tasks)

        print(f"Fetched {len(concepts)} concepts concurrently:")
        for c in concepts:
            print(f"  {c['concept_id']}: {c['concept_name']}")


async def parallel_searches() -> None:
    """Demonstrate parallel search operations."""
    print("\n=== Parallel Searches ===")

    async with omophub.AsyncOMOPHub() as client:
        # Run multiple searches in parallel. ``search.basic`` returns a
        # flat list of concept dicts for the current page; for the full
        # total count we iterate across pages via ``basic_iter``.
        search_terms = ["diabetes", "hypertension", "asthma", "depression"]

        async def page_count(term: str) -> tuple[str, int]:
            concepts = await client.search.basic(term, page_size=50)
            return term, len(concepts)

        tasks = [page_count(term) for term in search_terms]
        results = await asyncio.gather(*tasks)

        print("First-page hit counts:")
        for term, count in results:
            print(f"  '{term}': {count} concepts")


async def main() -> None:
    """Run all async examples."""
    await basic_async_usage()
    await concurrent_requests()
    await parallel_searches()


if __name__ == "__main__":
    asyncio.run(main())
