"""Search type definitions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypedDict

from typing_extensions import NotRequired, Required

if TYPE_CHECKING:
    from .concept import Concept


class Suggestion(TypedDict, total=False):
    """Autocomplete suggestion, including optional enriched concept metadata."""

    suggestion: Required[str]
    concept_id: int
    concept_code: str
    vocabulary_id: str
    domain_id: str
    concept_class_id: str
    standard_concept: str | None
    context: NotRequired[dict[str, str]]


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


class SimilarConceptScores(TypedDict, total=False):
    """Per-signal scores behind a fused similarity score."""

    semantic: float
    lexical: float
    hybrid: float


class SimilarConcept(TypedDict):
    """A concept similar to the query concept."""

    concept_id: int
    concept_name: str
    domain_id: str
    vocabulary_id: str
    concept_class_id: str
    standard_concept: str | None
    concept_code: str
    # Optional because ``include_scores=False`` removes it. It was typed as
    # required, which made that documented option a type error.
    similarity_score: NotRequired[float]
    matched_text: NotRequired[str]
    scores: NotRequired[SimilarConceptScores]
    explanation: NotRequired[str]
    #: Deprecated alias for ``explanation``, still emitted by the API for one
    #: release. Read ``explanation``.
    similarity_explanation: NotRequired[str]


class SimilarSearchMetadata(TypedDict, total=False):
    """Metadata for similar concept search."""

    original_query: str
    algorithm_used: str
    similarity_threshold: float
    #: How many concepts cleared ``similarity_threshold`` inside the bounded
    #: retrieval pool - not how many were evaluated. The pool holds up to 500
    #: and everything below the threshold is discarded before this is counted.
    total_candidates: int
    results_returned: int
    processing_time_ms: int
    embedding_latency_ms: int
    #: True when retrieval hit its candidate bound, so ``total_candidates`` and
    #: the pagination totals count only what qualified inside the pool that was
    #: searched, not the whole corpus.
    totals_are_lower_bound: bool
    #: The algorithm that was requested, when a fallback served the request
    #: instead (``hybrid`` degrading to ``lexical`` when the embedding service
    #: is unavailable).
    degraded_from: str
    source_concept_id: int


class SourceConcept(TypedDict, total=False):
    """The reference concept a similarity search started from."""

    concept_id: int
    concept_name: str
    concept_code: str
    vocabulary_id: str
    domain_id: str
    concept_class_id: str
    standard_concept: str | None


class SimilarSearchPagination(TypedDict, total=False):
    """Pagination for a similarity search.

    Lifted here from the response envelope's ``meta``. Page while ``has_next``
    is true rather than comparing ``page`` to ``total_pages``: every algorithm
    ranks a bounded candidate pool, so the totals may be lower bounds (see
    ``SimilarSearchMetadata.totals_are_lower_bound``).
    """

    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class SimilarSearchResult(TypedDict):
    """Result from similar concept search."""

    similar_concepts: list[SimilarConcept]
    search_metadata: SimilarSearchMetadata
    source_concept: NotRequired[SourceConcept]
    pagination: NotRequired[SimilarSearchPagination]


# ---------------------------------------------------------------------------
# Bulk search types
# ---------------------------------------------------------------------------


class BulkSearchInput(TypedDict, total=False):
    """Input for a single query in a bulk lexical search."""

    search_id: Required[str]
    query: Required[str]
    vocabulary_ids: list[str]
    domain_ids: list[str]
    concept_class_ids: list[str]
    standard_concept: str
    include_invalid: bool
    page_size: int


class BulkSearchDefaults(TypedDict, total=False):
    """Default filters applied to all searches in a bulk lexical request."""

    vocabulary_ids: list[str]
    domain_ids: list[str]
    concept_class_ids: list[str]
    standard_concept: str
    include_invalid: bool
    page_size: int


class BulkSearchResultItem(TypedDict):
    """Result for a single query in a bulk lexical search."""

    search_id: str
    query: str
    results: list[dict[str, Any]]
    status: str  # "completed" | "failed"
    error: NotRequired[str]
    duration: NotRequired[int]


class BulkSearchResponse(TypedDict):
    """Response from bulk lexical search."""

    results: list[BulkSearchResultItem]
    total_searches: int
    completed_searches: int
    failed_searches: int


class BulkSemanticSearchInput(TypedDict, total=False):
    """Input for a single query in a bulk semantic search."""

    search_id: Required[str]
    query: Required[str]  # 1-500 characters
    page_size: int
    threshold: float
    vocabulary_ids: list[str]
    domain_ids: list[str]
    standard_concept: str
    concept_class_id: str


class BulkSemanticSearchDefaults(TypedDict, total=False):
    """Default filters applied to all searches in a bulk semantic request."""

    page_size: int
    threshold: float
    vocabulary_ids: list[str]
    domain_ids: list[str]
    standard_concept: str
    concept_class_id: str


class QueryEnhancement(TypedDict, total=False):
    """Query enhancement info from semantic search."""

    original_query: str
    enhanced_query: str
    abbreviations_expanded: list[str]
    misspellings_corrected: list[str]


class BulkSemanticSearchResultItem(TypedDict):
    """Result for a single query in a bulk semantic search."""

    search_id: str
    query: str
    results: list[dict[str, Any]]
    status: str  # "completed" | "failed"
    error: NotRequired[str]
    similarity_threshold: NotRequired[float]
    result_count: NotRequired[int]
    duration: NotRequired[int]
    query_enhancement: NotRequired[QueryEnhancement]


class BulkSemanticSearchResponse(TypedDict):
    """Response from bulk semantic search."""

    results: list[BulkSemanticSearchResultItem]
    total_searches: int
    completed_count: int
    failed_count: int
    total_duration: NotRequired[int]


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
