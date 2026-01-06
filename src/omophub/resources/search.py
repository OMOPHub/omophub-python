"""Search resource implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypedDict

from .._pagination import DEFAULT_PAGE_SIZE, paginate_sync

if TYPE_CHECKING:
    from collections.abc import Iterator

    from .._request import AsyncRequest, Request
    from ..types.common import PaginationMeta
    from ..types.concept import Concept
    from ..types.search import SearchResult, Suggestion


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
        page_size: int = DEFAULT_PAGE_SIZE,
        **kwargs: Any,
    ) -> Iterator[Concept]:
        """Iterate through all search results with auto-pagination.

        Args:
            query: Search query string
            vocabulary_ids: Filter by vocabulary IDs
            domain_ids: Filter by domain IDs
            page_size: Results per page
            **kwargs: Additional search parameters

        Yields:
            Individual concepts from all pages
        """

        def fetch_page(
            page: int, size: int
        ) -> tuple[list[Concept], PaginationMeta | None]:
            result = self.basic(
                query,
                vocabulary_ids=vocabulary_ids,
                domain_ids=domain_ids,
                page=page,
                page_size=size,
                **kwargs,
            )
            concepts = (
                result.get("concepts", result) if isinstance(result, dict) else result
            )
            meta = (
                result.get("meta", {}).get("pagination")
                if isinstance(result, dict)
                else None
            )
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
