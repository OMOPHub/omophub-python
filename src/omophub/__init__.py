"""
OMOPHub Python SDK.

A Python client for the OMOPHub Medical Vocabulary API.

Example:
    >>> import omophub
    >>> client = omophub.OMOPHub(api_key="oh_xxxxxxxxx")
    >>> concept = client.concepts.get(201826)
    >>> print(concept["concept_name"])
    "Type 2 diabetes mellitus"

Async Example:
    >>> import omophub
    >>> async with omophub.AsyncOMOPHub(api_key="oh_xxx") as client:
    ...     concept = await client.concepts.get(201826)
"""

from ._client import AsyncOMOPHub, OMOPHub
from ._config import api_key, api_url, max_retries, timeout
from ._exceptions import (
    APIError,
    AuthenticationError,
    ConnectionError,
    NotFoundError,
    OMOPHubError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ValidationError,
)
from ._version import __version__

# Re-export commonly used types
from .types import (
    Ancestor,
    BatchConceptResult,
    Concept,
    ConceptSummary,
    Descendant,
    Domain,
    DomainStats,
    HierarchySummary,
    Mapping,
    MappingQuality,
    MappingSummary,
    PaginationMeta,
    Relationship,
    RelationshipType,
    SearchFacets,
    SearchResult,
    Suggestion,
    Vocabulary,
    VocabularyStats,
)

__all__ = [
    "APIError",
    "Ancestor",
    "AsyncOMOPHub",
    "AuthenticationError",
    "BatchConceptResult",
    # Types
    "Concept",
    "ConceptSummary",
    "ConnectionError",
    "Descendant",
    "Domain",
    "DomainStats",
    "HierarchySummary",
    "Mapping",
    "MappingQuality",
    "MappingSummary",
    "NotFoundError",
    # Clients
    "OMOPHub",
    # Exceptions
    "OMOPHubError",
    "PaginationMeta",
    "RateLimitError",
    "Relationship",
    "RelationshipType",
    "SearchFacets",
    "SearchResult",
    "ServerError",
    "Suggestion",
    "TimeoutError",
    "ValidationError",
    "Vocabulary",
    "VocabularyStats",
    # Version
    "__version__",
    # Configuration
    "api_key",
    "api_url",
    "max_retries",
    "timeout",
]
