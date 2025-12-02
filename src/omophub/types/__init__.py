"""Type definitions for the OMOPHub SDK."""

from .common import (
    APIResponse,
    ErrorDetail,
    ErrorResponse,
    PaginationMeta,
    PaginationParams,
    ResponseMeta,
)
from .concept import (
    BatchConceptResult,
    Concept,
    ConceptSummary,
    RelatedConcept,
    Synonym,
)
from .domain import Domain, DomainCategory, DomainStats, DomainSummary
from .hierarchy import (
    Ancestor,
    Descendant,
    HierarchyPath,
    HierarchySummary,
)
from .mapping import (
    Mapping,
    MappingContext,
    MappingQuality,
    MappingSummary,
)
from .relationship import (
    Relationship,
    RelationshipSummary,
    RelationshipType,
)
from .search import (
    SearchFacet,
    SearchFacets,
    SearchMetadata,
    SearchResult,
    Suggestion,
)
from .vocabulary import (
    Vocabulary,
    VocabularyDomain,
    VocabularyStats,
    VocabularySummary,
)

__all__ = [
    # Common
    "APIResponse",
    # Hierarchy
    "Ancestor",
    "BatchConceptResult",
    # Concept
    "Concept",
    "ConceptSummary",
    "Descendant",
    # Domain
    "Domain",
    "DomainCategory",
    "DomainStats",
    "DomainSummary",
    "ErrorDetail",
    "ErrorResponse",
    "HierarchyPath",
    "HierarchySummary",
    # Mapping
    "Mapping",
    "MappingContext",
    "MappingQuality",
    "MappingSummary",
    "PaginationMeta",
    "PaginationParams",
    "RelatedConcept",
    # Relationship
    "Relationship",
    "RelationshipSummary",
    "RelationshipType",
    "ResponseMeta",
    # Search
    "SearchFacet",
    "SearchFacets",
    "SearchMetadata",
    "SearchResult",
    "Suggestion",
    "Synonym",
    # Vocabulary
    "Vocabulary",
    "VocabularyDomain",
    "VocabularyStats",
    "VocabularySummary",
]
