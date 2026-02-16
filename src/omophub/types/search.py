"""Search type definitions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypedDict

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


class SemanticSearchResult(TypedDict):
    """Result from semantic concept search."""

    concept_id: int
    concept_name: str
    domain_id: str
    vocabulary_id: str
    concept_class_id: str
    standard_concept: str | None
    concept_code: str
    similarity_score: float
    matched_text: str


class SemanticSearchMeta(TypedDict, total=False):
    """Metadata for semantic search."""

    query: str
    total_results: int
    filters_applied: dict[str, Any]


class SimilarConcept(TypedDict):
    """A concept similar to the query concept."""

    concept_id: int
    concept_name: str
    domain_id: str
    vocabulary_id: str
    concept_class_id: str
    standard_concept: str | None
    concept_code: str
    similarity_score: float
    matched_text: NotRequired[str]
    similarity_explanation: NotRequired[str]


class SimilarSearchMetadata(TypedDict, total=False):
    """Metadata for similar concept search."""

    original_query: str
    algorithm_used: str
    similarity_threshold: float
    total_candidates: int
    results_returned: int
    processing_time_ms: int
    embedding_latency_ms: int


class SimilarSearchResult(TypedDict):
    """Result from similar concept search."""

    similar_concepts: list[SimilarConcept]
    search_metadata: SimilarSearchMetadata


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
