"""Search resource implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, TypedDict

from .._pagination import DEFAULT_PAGE_SIZE, paginate_sync

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from .._request import AsyncRequest, Request
    from ..types.common import PaginationMeta
    from ..types.concept import Concept
    from ..types.search import (
        SearchResult,
        SemanticSearchResult,
        SimilarSearchResult,
        Suggestion,
    )


class BasicSearchParams(TypedDict, total=False):
    """Parameters for basic search."""

    query: str
    vocabulary_ids: list[str]
    domain_ids: list[str]
    concept_class_ids: list[str]
    standard_concept: str
    include_synonyms: bool
    include_invalid: bool
    min_score: float
    exact_match: bool
    page: int
    page_size: int
    sort_by: str
    sort_order: str


class AdvancedSearchParams(TypedDict, total=False):
    """Parameters for advanced search."""

    query: str
    vocabulary_ids: list[str]
    domain_ids: list[str]
    concept_class_ids: list[str]
    standard_concepts_only: bool
    include_invalid: bool
    relationship_filters: list[dict[str, Any]]
    date_range: dict[str, str]
    page: int
    page_size: int


class Search:
    """Synchronous search resource."""

    def __init__(self, request: Request[Any]) -> None:
        self._request = request

    def basic(
        self,
        query: str,
        *,
        vocabulary_ids: list[str] | None = None,
        domain_ids: list[str] | None = None,
        concept_class_ids: list[str] | None = None,
        standard_concept: str | None = None,
        include_synonyms: bool = False,
        include_invalid: bool = False,
        min_score: float | None = None,
        exact_match: bool = False,
        page: int = 1,
        page_size: int = 20,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> dict[str, Any]:
        """Basic concept search.

        Args:
            query: Search query string
            vocabulary_ids: Filter by vocabulary IDs
            domain_ids: Filter by domain IDs
            concept_class_ids: Filter by concept class IDs
            standard_concept: Filter by standard concept ("S", "C", or None)
            include_synonyms: Search in synonyms
            include_invalid: Include invalid concepts
            min_score: Minimum relevance score
            exact_match: Require exact match
            page: Page number (1-based)
            page_size: Results per page
            sort_by: Sort field
            sort_order: Sort order ("asc" or "desc")

        Returns:
            Search results with pagination
        """
        params: dict[str, Any] = {
            "query": query,
            "page": page,
            "page_size": page_size,
        }
        if vocabulary_ids:
            params["vocabulary_ids"] = ",".join(vocabulary_ids)
        if domain_ids:
            params["domain_ids"] = ",".join(domain_ids)
        if concept_class_ids:
            params["concept_class_ids"] = ",".join(concept_class_ids)
        if standard_concept:
            params["standard_concept"] = standard_concept
        if include_synonyms:
            params["include_synonyms"] = "true"
        if include_invalid:
            params["include_invalid"] = "true"
        if min_score is not None:
            params["min_score"] = min_score
        if exact_match:
            params["exact_match"] = "true"
        if sort_by:
            params["sort_by"] = sort_by
        if sort_order:
            params["sort_order"] = sort_order

        return self._request.get("/search/concepts", params=params)

    def basic_iter(
        self,
        query: str,
        *,
        vocabulary_ids: list[str] | None = None,
        domain_ids: list[str] | None = None,
        concept_class_ids: list[str] | None = None,
        standard_concept: str | None = None,
        include_synonyms: bool = False,
        include_invalid: bool = False,
        min_score: float | None = None,
        exact_match: bool = False,
        page_size: int = DEFAULT_PAGE_SIZE,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> Iterator[Concept]:
        """Iterate through all search results with auto-pagination.

        Args:
            query: Search query string
            vocabulary_ids: Filter by vocabulary IDs
            domain_ids: Filter by domain IDs
            concept_class_ids: Filter by concept class IDs
            standard_concept: Filter by standard concept ("S", "C", or None)
            include_synonyms: Search in synonyms
            include_invalid: Include invalid concepts
            min_score: Minimum relevance score
            exact_match: Require exact match
            page_size: Results per page
            sort_by: Sort field
            sort_order: Sort order ("asc" or "desc")

        Yields:
            Individual concepts from all pages
        """

        def fetch_page(
            page: int, size: int
        ) -> tuple[list[Concept], PaginationMeta | None]:
            # Build params manually to use get_raw() for full response with meta
            params: dict[str, Any] = {
                "query": query,
                "page": page,
                "page_size": size,
            }
            if vocabulary_ids:
                params["vocabulary_ids"] = ",".join(vocabulary_ids)
            if domain_ids:
                params["domain_ids"] = ",".join(domain_ids)
            if concept_class_ids:
                params["concept_class_ids"] = ",".join(concept_class_ids)
            if standard_concept:
                params["standard_concept"] = standard_concept
            if include_synonyms:
                params["include_synonyms"] = "true"
            if include_invalid:
                params["include_invalid"] = "true"
            if min_score is not None:
                params["min_score"] = min_score
            if exact_match:
                params["exact_match"] = "true"
            if sort_by:
                params["sort_by"] = sort_by
            if sort_order:
                params["sort_order"] = sort_order

            # Use get_raw() to preserve pagination metadata
            result = self._request.get_raw("/search/concepts", params=params)

            # Extract concepts from 'data' field (may be list or dict with 'concepts')
            data = result.get("data", [])
            concepts = data.get("concepts", data) if isinstance(data, dict) else data
            meta = result.get("meta", {}).get("pagination")
            return concepts, meta

        yield from paginate_sync(fetch_page, page_size)

    def advanced(
        self,
        query: str,
        *,
        vocabulary_ids: list[str] | None = None,
        domain_ids: list[str] | None = None,
        concept_class_ids: list[str] | None = None,
        standard_concepts_only: bool = False,
        include_invalid: bool = False,
        relationship_filters: list[dict[str, Any]] | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> SearchResult:
        """Advanced concept search with facets.

        Args:
            query: Search query string
            vocabulary_ids: Filter by vocabulary IDs
            domain_ids: Filter by domain IDs
            concept_class_ids: Filter by concept class IDs
            standard_concepts_only: Only return standard concepts
            include_invalid: Include invalid concepts
            relationship_filters: Relationship-based filters
            page: Page number (1-based)
            page_size: Results per page

        Returns:
            Search results with facets and metadata
        """
        body: dict[str, Any] = {"query": query}
        if vocabulary_ids:
            body["vocabulary_ids"] = vocabulary_ids
        if domain_ids:
            body["domain_ids"] = domain_ids
        if concept_class_ids:
            body["concept_class_ids"] = concept_class_ids
        if standard_concepts_only:
            body["standard_concepts_only"] = True
        if include_invalid:
            body["include_invalid"] = True
        if relationship_filters:
            body["relationship_filters"] = relationship_filters
        if page != 1:
            body["page"] = page
        if page_size != 20:
            body["page_size"] = page_size

        return self._request.post("/search/advanced", json_data=body)

    def autocomplete(
        self,
        query: str,
        *,
        vocabulary_ids: list[str] | None = None,
        domains: list[str] | None = None,
        page_size: int = 10,
    ) -> list[Suggestion]:
        """Get autocomplete suggestions.

        Args:
            query: Partial query string
            vocabulary_ids: Filter by vocabulary IDs
            domains: Filter by domains
            page_size: Maximum suggestions to return

        Returns:
            Autocomplete suggestions
        """
        params: dict[str, Any] = {"query": query, "page_size": page_size}
        if vocabulary_ids:
            params["vocabulary_ids"] = ",".join(vocabulary_ids)
        if domains:
            params["domains"] = ",".join(domains)

        return self._request.get("/search/suggest", params=params)

    def semantic(
        self,
        query: str,
        *,
        vocabulary_ids: list[str] | None = None,
        domain_ids: list[str] | None = None,
        standard_concept: Literal["S", "C"] | None = None,
        concept_class_id: str | None = None,
        threshold: float | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """Semantic concept search using neural embeddings.

        Args:
            query: Natural language search query
            vocabulary_ids: Filter by vocabulary IDs
            domain_ids: Filter by domain IDs
            standard_concept: Filter by standard concept flag ('S' or 'C')
            concept_class_id: Filter by concept class
            threshold: Minimum similarity threshold (0.0-1.0, default 0.3)
            page: Page number (1-based)
            page_size: Results per page (max 100)

        Returns:
            Semantic search results with similarity scores
        """
        params: dict[str, Any] = {"query": query, "page": page, "page_size": page_size}
        if vocabulary_ids:
            params["vocabulary_ids"] = ",".join(vocabulary_ids)
        if domain_ids:
            params["domain_ids"] = ",".join(domain_ids)
        if standard_concept:
            params["standard_concept"] = standard_concept
        if concept_class_id:
            params["concept_class_id"] = concept_class_id
        if threshold is not None:
            params["threshold"] = threshold

        return self._request.get("/concepts/semantic-search", params=params)

    def semantic_iter(
        self,
        query: str,
        *,
        vocabulary_ids: list[str] | None = None,
        domain_ids: list[str] | None = None,
        standard_concept: Literal["S", "C"] | None = None,
        concept_class_id: str | None = None,
        threshold: float | None = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> Iterator[SemanticSearchResult]:
        """Iterate through all semantic search results with auto-pagination.

        Args:
            query: Natural language search query
            vocabulary_ids: Filter by vocabulary IDs
            domain_ids: Filter by domain IDs
            standard_concept: Filter by standard concept flag ('S' or 'C')
            concept_class_id: Filter by concept class
            threshold: Minimum similarity threshold (0.0-1.0)
            page_size: Results per page

        Yields:
            Individual semantic search results from all pages
        """

        def fetch_page(
            page: int, size: int
        ) -> tuple[list[SemanticSearchResult], PaginationMeta | None]:
            params: dict[str, Any] = {
                "query": query,
                "page": page,
                "page_size": size,
            }
            if vocabulary_ids:
                params["vocabulary_ids"] = ",".join(vocabulary_ids)
            if domain_ids:
                params["domain_ids"] = ",".join(domain_ids)
            if standard_concept:
                params["standard_concept"] = standard_concept
            if concept_class_id:
                params["concept_class_id"] = concept_class_id
            if threshold is not None:
                params["threshold"] = threshold

            result = self._request.get_raw("/concepts/semantic-search", params=params)

            data = result.get("data", [])
            results = data.get("results", data) if isinstance(data, dict) else data
            meta = result.get("meta", {}).get("pagination")
            return results, meta

        yield from paginate_sync(fetch_page, page_size)

    def similar(
        self,
        *,
        concept_id: int | None = None,
        concept_name: str | None = None,
        query: str | None = None,
        algorithm: Literal["semantic", "lexical", "hybrid"] = "hybrid",
        similarity_threshold: float = 0.7,
        page_size: int = 20,
        vocabulary_ids: list[str] | None = None,
        domain_ids: list[str] | None = None,
        standard_concept: Literal["S", "C", "N"] | None = None,
        include_invalid: bool | None = None,
        include_scores: bool | None = None,
        include_explanations: bool | None = None,
    ) -> SimilarSearchResult:
        """Find concepts similar to a reference concept or query.

        Must provide exactly one of: concept_id, concept_name, or query.

        Args:
            concept_id: Find concepts similar to this concept ID
            concept_name: Find concepts similar to this name
            query: Natural language query for semantic similarity
            algorithm: 'semantic' (neural), 'lexical' (text), or 'hybrid' (both)
            similarity_threshold: Minimum similarity (0.0-1.0)
            page_size: Max results to return (max 1000)
            vocabulary_ids: Filter by vocabulary IDs
            domain_ids: Filter by domain IDs
            standard_concept: Filter by standard concept flag
            include_invalid: Include invalid/deprecated concepts
            include_scores: Include detailed similarity scores
            include_explanations: Include similarity explanations

        Returns:
            Similar concepts with similarity scores and metadata

        Raises:
            ValueError: If not exactly one of concept_id, concept_name, or query
                is provided.

        Note:
            When algorithm='semantic', only single vocabulary/domain filter supported.
        """
        # Validate exactly one input source provided
        input_count = sum(x is not None for x in [concept_id, concept_name, query])
        if input_count != 1:
            raise ValueError(
                "Exactly one of concept_id, concept_name, or query must be provided"
            )

        body: dict[str, Any] = {
            "algorithm": algorithm,
            "similarity_threshold": similarity_threshold,
        }
        if concept_id is not None:
            body["concept_id"] = concept_id
        if concept_name is not None:
            body["concept_name"] = concept_name
        if query is not None:
            body["query"] = query
        if page_size != 20:
            body["page_size"] = page_size
        if vocabulary_ids:
            body["vocabulary_ids"] = vocabulary_ids
        if domain_ids:
            body["domain_ids"] = domain_ids
        if standard_concept:
            body["standard_concept"] = standard_concept
        if include_invalid is not None:
            body["include_invalid"] = include_invalid
        if include_scores is not None:
            body["include_scores"] = include_scores
        if include_explanations is not None:
            body["include_explanations"] = include_explanations

        return self._request.post("/search/similar", json_data=body)


class AsyncSearch:
    """Asynchronous search resource."""

    def __init__(self, request: AsyncRequest[Any]) -> None:
        self._request = request

    async def basic(
        self,
        query: str,
        *,
        vocabulary_ids: list[str] | None = None,
        domain_ids: list[str] | None = None,
        concept_class_ids: list[str] | None = None,
        standard_concept: str | None = None,
        include_synonyms: bool = False,
        include_invalid: bool = False,
        min_score: float | None = None,
        exact_match: bool = False,
        page: int = 1,
        page_size: int = 20,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> dict[str, Any]:
        """Basic concept search."""
        params: dict[str, Any] = {
            "query": query,
            "page": page,
            "page_size": page_size,
        }
        if vocabulary_ids:
            params["vocabulary_ids"] = ",".join(vocabulary_ids)
        if domain_ids:
            params["domain_ids"] = ",".join(domain_ids)
        if concept_class_ids:
            params["concept_class_ids"] = ",".join(concept_class_ids)
        if standard_concept:
            params["standard_concept"] = standard_concept
        if include_synonyms:
            params["include_synonyms"] = "true"
        if include_invalid:
            params["include_invalid"] = "true"
        if min_score is not None:
            params["min_score"] = min_score
        if exact_match:
            params["exact_match"] = "true"
        if sort_by:
            params["sort_by"] = sort_by
        if sort_order:
            params["sort_order"] = sort_order

        return await self._request.get("/search/concepts", params=params)

    async def advanced(
        self,
        query: str,
        *,
        vocabulary_ids: list[str] | None = None,
        domain_ids: list[str] | None = None,
        concept_class_ids: list[str] | None = None,
        standard_concepts_only: bool = False,
        include_invalid: bool = False,
        relationship_filters: list[dict[str, Any]] | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> SearchResult:
        """Advanced concept search with facets."""
        body: dict[str, Any] = {"query": query}
        if vocabulary_ids:
            body["vocabulary_ids"] = vocabulary_ids
        if domain_ids:
            body["domain_ids"] = domain_ids
        if concept_class_ids:
            body["concept_class_ids"] = concept_class_ids
        if standard_concepts_only:
            body["standard_concepts_only"] = True
        if include_invalid:
            body["include_invalid"] = True
        if relationship_filters:
            body["relationship_filters"] = relationship_filters
        if page != 1:
            body["page"] = page
        if page_size != 20:
            body["page_size"] = page_size

        return await self._request.post("/search/advanced", json_data=body)

    async def autocomplete(
        self,
        query: str,
        *,
        vocabulary_ids: list[str] | None = None,
        domains: list[str] | None = None,
        page_size: int = 10,
    ) -> list[Suggestion]:
        """Get autocomplete suggestions."""
        params: dict[str, Any] = {"query": query, "page_size": page_size}
        if vocabulary_ids:
            params["vocabulary_ids"] = ",".join(vocabulary_ids)
        if domains:
            params["domains"] = ",".join(domains)

        return await self._request.get("/search/suggest", params=params)

    async def semantic(
        self,
        query: str,
        *,
        vocabulary_ids: list[str] | None = None,
        domain_ids: list[str] | None = None,
        standard_concept: Literal["S", "C"] | None = None,
        concept_class_id: str | None = None,
        threshold: float | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """Semantic concept search using neural embeddings."""
        params: dict[str, Any] = {"query": query, "page": page, "page_size": page_size}
        if vocabulary_ids:
            params["vocabulary_ids"] = ",".join(vocabulary_ids)
        if domain_ids:
            params["domain_ids"] = ",".join(domain_ids)
        if standard_concept:
            params["standard_concept"] = standard_concept
        if concept_class_id:
            params["concept_class_id"] = concept_class_id
        if threshold is not None:
            params["threshold"] = threshold

        return await self._request.get("/concepts/semantic-search", params=params)

    async def semantic_iter(
        self,
        query: str,
        *,
        vocabulary_ids: list[str] | None = None,
        domain_ids: list[str] | None = None,
        standard_concept: Literal["S", "C"] | None = None,
        concept_class_id: str | None = None,
        threshold: float | None = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> AsyncIterator[SemanticSearchResult]:
        """Iterate through all semantic search results with auto-pagination."""
        page = 1

        while True:
            params: dict[str, Any] = {
                "query": query,
                "page": page,
                "page_size": page_size,
            }
            if vocabulary_ids:
                params["vocabulary_ids"] = ",".join(vocabulary_ids)
            if domain_ids:
                params["domain_ids"] = ",".join(domain_ids)
            if standard_concept:
                params["standard_concept"] = standard_concept
            if concept_class_id:
                params["concept_class_id"] = concept_class_id
            if threshold is not None:
                params["threshold"] = threshold

            result = await self._request.get_raw(
                "/concepts/semantic-search", params=params
            )

            data = result.get("data", [])
            results: list[SemanticSearchResult] = (
                data.get("results", data) if isinstance(data, dict) else data
            )
            meta: PaginationMeta | None = result.get("meta", {}).get("pagination")

            for item in results:
                yield item

            if meta is None or not meta.get("has_next", False):
                break

            page += 1

    async def similar(
        self,
        *,
        concept_id: int | None = None,
        concept_name: str | None = None,
        query: str | None = None,
        algorithm: Literal["semantic", "lexical", "hybrid"] = "hybrid",
        similarity_threshold: float = 0.7,
        page_size: int = 20,
        vocabulary_ids: list[str] | None = None,
        domain_ids: list[str] | None = None,
        standard_concept: Literal["S", "C", "N"] | None = None,
        include_invalid: bool | None = None,
        include_scores: bool | None = None,
        include_explanations: bool | None = None,
    ) -> SimilarSearchResult:
        """Find concepts similar to a reference concept or query.

        Must provide exactly one of: concept_id, concept_name, or query.

        Raises:
            ValueError: If not exactly one of concept_id, concept_name, or query
                is provided.
        """
        # Validate exactly one input source provided
        input_count = sum(x is not None for x in [concept_id, concept_name, query])
        if input_count != 1:
            raise ValueError(
                "Exactly one of concept_id, concept_name, or query must be provided"
            )

        body: dict[str, Any] = {
            "algorithm": algorithm,
            "similarity_threshold": similarity_threshold,
        }
        if concept_id is not None:
            body["concept_id"] = concept_id
        if concept_name is not None:
            body["concept_name"] = concept_name
        if query is not None:
            body["query"] = query
        if page_size != 20:
            body["page_size"] = page_size
        if vocabulary_ids:
            body["vocabulary_ids"] = vocabulary_ids
        if domain_ids:
            body["domain_ids"] = domain_ids
        if standard_concept:
            body["standard_concept"] = standard_concept
        if include_invalid is not None:
            body["include_invalid"] = include_invalid
        if include_scores is not None:
            body["include_scores"] = include_scores
        if include_explanations is not None:
            body["include_explanations"] = include_explanations

        return await self._request.post("/search/similar", json_data=body)
