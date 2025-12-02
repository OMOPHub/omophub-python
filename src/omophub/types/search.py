"""Search type definitions."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .concept import Concept


class Suggestion(TypedDict):
    """Autocomplete suggestion."""

    suggestion: str
    type: NotRequired[str]
    match_type: NotRequired[str]
    match_score: NotRequired[float]
    concept_id: NotRequired[int]
    vocabulary_id: NotRequired[str]


class SearchFacet(TypedDict):
    """Search facet with count."""

    value: str
    count: int


class SearchFacets(TypedDict, total=False):
    """Faceted search results."""

    vocabularies: list[SearchFacet]
    domains: list[SearchFacet]
    concept_classes: list[SearchFacet]


class SearchMetadata(TypedDict, total=False):
    """Search operation metadata."""

    query_time_ms: int
    total_results: int
    max_relevance_score: float
    search_algorithm: str


class SearchResult(TypedDict):
    """Search result with concepts and metadata."""

    concepts: list[Concept]
    facets: NotRequired[SearchFacets]
    search_metadata: NotRequired[SearchMetadata]
