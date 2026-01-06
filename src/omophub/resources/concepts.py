"""Concepts resource implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypedDict

if TYPE_CHECKING:
    from .._request import AsyncRequest, Request
    from ..types.concept import BatchConceptResult, Concept


class GetConceptParams(TypedDict, total=False):
    """Parameters for getting a concept."""

    include_relationships: bool
    include_synonyms: bool


class BatchConceptParams(TypedDict, total=False):
    """Parameters for batch concept retrieval."""

    concept_ids: list[int]
    include_relationships: bool
    include_synonyms: bool
    include_mappings: bool
    vocabulary_filter: list[str]
    standard_only: bool


class SuggestParams(TypedDict, total=False):
    """Parameters for concept suggestions."""

    query: str
    page: int
    page_size: int
    vocabulary_ids: list[str]
    domain_ids: list[str]
    vocab_release: str


class RelatedParams(TypedDict, total=False):
    """Parameters for related concepts."""

    relationship_types: list[str]
    min_score: float
    page_size: int


class RelationshipsParams(TypedDict, total=False):
    """Parameters for concept relationships."""

    relationship_type: str
    target_vocabulary: str
    include_invalid: bool
    page: int
    page_size: int


class Concepts:
    """Synchronous concepts resource."""

    def __init__(self, request: Request[Any]) -> None:
        self._request = request

    def get(
        self,
        concept_id: int,
        *,
        include_relationships: bool = False,
        include_synonyms: bool = False,
        include_hierarchy: bool = False,
        vocab_release: str | None = None,
    ) -> Concept:
        """Get a concept by ID.

        Args:
            concept_id: The OMOP concept ID
            include_relationships: Include related concepts (parents/children)
            include_synonyms: Include concept synonyms
            include_hierarchy: Include hierarchy information
            vocab_release: Specific vocabulary release (e.g., "2025.2")

        Returns:
            The concept data
        """
        params: dict[str, Any] = {}
        if include_relationships:
            params["include_relationships"] = "true"
        if include_synonyms:
            params["include_synonyms"] = "true"
        if include_hierarchy:
            params["include_hierarchy"] = "true"
        if vocab_release:
            params["vocab_release"] = vocab_release

        return self._request.get(f"/concepts/{concept_id}", params=params or None)

    def get_by_code(
        self,
        vocabulary_id: str,
        concept_code: str,
        *,
        include_relationships: bool = False,
        include_synonyms: bool = False,
        include_hierarchy: bool = False,
        vocab_release: str | None = None,
    ) -> Concept:
        """Get a concept by vocabulary and code.

        Args:
            vocabulary_id: The vocabulary ID (e.g., "SNOMED", "ICD10CM")
            concept_code: The concept code within the vocabulary
            include_relationships: Include related concepts (parents/children)
            include_synonyms: Include concept synonyms
            include_hierarchy: Include hierarchy information
            vocab_release: Specific vocabulary release (e.g., "2025.2")

        Returns:
            The concept data with optional relationships and synonyms
        """
        params: dict[str, Any] = {}
        if include_relationships:
            params["include_relationships"] = "true"
        if include_synonyms:
            params["include_synonyms"] = "true"
        if include_hierarchy:
            params["include_hierarchy"] = "true"
        if vocab_release:
            params["vocab_release"] = vocab_release

        return self._request.get(
            f"/concepts/by-code/{vocabulary_id}/{concept_code}",
            params=params or None,
        )

    def batch(
        self,
        concept_ids: list[int],
        *,
        include_relationships: bool = False,
        include_synonyms: bool = False,
        include_mappings: bool = False,
        vocabulary_filter: list[str] | None = None,
        standard_only: bool = True,
    ) -> BatchConceptResult:
        """Get multiple concepts by IDs.

        Args:
            concept_ids: List of concept IDs (max 100)
            include_relationships: Include related concepts
            include_synonyms: Include concept synonyms
            include_mappings: Include concept mappings
            vocabulary_filter: Filter results to specific vocabularies
            standard_only: Only return standard concepts (default True)

        Returns:
            Batch result with concepts and any failures
        """
        body: dict[str, Any] = {"concept_ids": concept_ids}
        if include_relationships:
            body["include_relationships"] = True
        if include_synonyms:
            body["include_synonyms"] = True
        if include_mappings:
            body["include_mappings"] = True
        if vocabulary_filter:
            body["vocabulary_filter"] = vocabulary_filter
        if standard_only:
            body["standard_only"] = True

        return self._request.post("/concepts/batch", json_data=body)

    def suggest(
        self,
        query: str,
        *,
        page: int = 1,
        page_size: int = 10,
        vocabulary_ids: list[str] | None = None,
        domain_ids: list[str] | None = None,
        vocab_release: str | None = None,
    ) -> dict[str, Any]:
        """Get concept suggestions (autocomplete).

        Args:
            query: Search query (min 2 characters, max 100 characters)
            page: Page number (default 1)
            page_size: Number of suggestions per page (default 10, max 100)
            vocabulary_ids: Filter to specific vocabularies (e.g., ["SNOMED", "ICD10CM"])
            domain_ids: Filter to specific domains (e.g., ["Condition", "Drug"])
            vocab_release: Specific vocabulary release (e.g., "2025.2")

        Returns:
            Paginated response with suggestions and pagination metadata
        """
        params: dict[str, Any] = {"query": query, "page": page, "page_size": page_size}
        if vocabulary_ids:
            params["vocabulary_ids"] = ",".join(vocabulary_ids)
        if domain_ids:
            params["domain_ids"] = ",".join(domain_ids)
        if vocab_release:
            params["vocab_release"] = vocab_release

        return self._request.get("/concepts/suggest", params=params)

    def related(
        self,
        concept_id: int,
        *,
        relationship_types: list[str] | None = None,
        min_score: float | None = None,
        page_size: int = 20,
        vocab_release: str | None = None,
    ) -> dict[str, Any]:
        """Get related concepts.

        Args:
            concept_id: The source concept ID
            relationship_types: Filter by relationship types (e.g., ["Is a", "Maps to"])
            min_score: Minimum relationship score (0.0-1.0)
            page_size: Maximum number of results (default 20, max 100)
            vocab_release: Specific vocabulary release (e.g., "2025.1")

        Returns:
            Related concepts with relationship scores
        """
        params: dict[str, Any] = {"page_size": page_size}
        if relationship_types:
            params["relationship_types"] = ",".join(relationship_types)
        if min_score is not None:
            params["min_score"] = min_score
        if vocab_release:
            params["vocab_release"] = vocab_release

        return self._request.get(f"/concepts/{concept_id}/related", params=params)

    def relationships(
        self,
        concept_id: int,
        *,
        relationship_ids: str | list[str] | None = None,
        vocabulary_ids: str | list[str] | None = None,
        domain_ids: str | list[str] | None = None,
        include_invalid: bool = False,
        standard_only: bool = False,
        include_reverse: bool = False,
        vocab_release: str | None = None,
    ) -> dict[str, Any]:
        """Get concept relationships.

        Args:
            concept_id: The concept ID
            relationship_ids: Filter by relationship type IDs (string or list)
            vocabulary_ids: Filter by target vocabulary IDs (string or list)
            domain_ids: Filter by target domain IDs (string or list)
            include_invalid: Include relationships to invalid concepts
            standard_only: Only include relationships to standard concepts
            include_reverse: Include reverse relationships
            vocab_release: Specific vocabulary release version

        Returns:
            Relationships data
        """
        params: dict[str, Any] = {}
        if relationship_ids:
            params["relationship_ids"] = (
                ",".join(relationship_ids)
                if isinstance(relationship_ids, list)
                else relationship_ids
            )
        if vocabulary_ids:
            params["vocabulary_ids"] = (
                ",".join(vocabulary_ids)
                if isinstance(vocabulary_ids, list)
                else vocabulary_ids
            )
        if domain_ids:
            params["domain_ids"] = (
                ",".join(domain_ids) if isinstance(domain_ids, list) else domain_ids
            )
        if include_invalid:
            params["include_invalid"] = "true"
        if standard_only:
            params["standard_only"] = "true"
        if include_reverse:
            params["include_reverse"] = "true"
        if vocab_release:
            params["vocab_release"] = vocab_release

        return self._request.get(f"/concepts/{concept_id}/relationships", params=params)

    def recommended(
        self,
        concept_ids: list[int],
        *,
        relationship_types: list[str] | None = None,
        vocabulary_ids: list[str] | None = None,
        domain_ids: list[str] | None = None,
        standard_only: bool = True,
        include_invalid: bool = False,
        page: int = 1,
        page_size: int = 100,
    ) -> dict[str, Any]:
        """Get recommended concepts using OHDSI Phoebe algorithm.

        Args:
            concept_ids: List of source concept IDs (1-100)
            relationship_types: Filter by relationship types (max 20)
            vocabulary_ids: Filter to specific vocabularies (max 50)
            domain_ids: Filter to specific domains (max 50)
            standard_only: Only return standard concepts (default True)
            include_invalid: Include invalid/deprecated concepts (default False)
            page: Page number (default 1)
            page_size: Results per page (default 100, max 1000)

        Returns:
            Recommendations grouped by source concept ID with pagination metadata
        """
        body: dict[str, Any] = {"concept_ids": concept_ids}
        if relationship_types:
            body["relationship_types"] = relationship_types
        if vocabulary_ids:
            body["vocabulary_ids"] = vocabulary_ids
        if domain_ids:
            body["domain_ids"] = domain_ids
        body["standard_only"] = standard_only
        body["include_invalid"] = include_invalid
        body["page"] = page
        body["page_size"] = page_size

        return self._request.post("/concepts/recommended", json_data=body)


class AsyncConcepts:
    """Asynchronous concepts resource."""

    def __init__(self, request: AsyncRequest[Any]) -> None:
        self._request = request

    async def get(
        self,
        concept_id: int,
        *,
        include_relationships: bool = False,
        include_synonyms: bool = False,
        include_hierarchy: bool = False,
        vocab_release: str | None = None,
    ) -> Concept:
        """Get a concept by ID.

        Args:
            concept_id: The OMOP concept ID
            include_relationships: Include related concepts (parents/children)
            include_synonyms: Include concept synonyms
            include_hierarchy: Include hierarchy information
            vocab_release: Specific vocabulary release (e.g., "2025.2")

        Returns:
            The concept data
        """
        params: dict[str, Any] = {}
        if include_relationships:
            params["include_relationships"] = "true"
        if include_synonyms:
            params["include_synonyms"] = "true"
        if include_hierarchy:
            params["include_hierarchy"] = "true"
        if vocab_release:
            params["vocab_release"] = vocab_release

        return await self._request.get(f"/concepts/{concept_id}", params=params or None)

    async def get_by_code(
        self,
        vocabulary_id: str,
        concept_code: str,
        *,
        include_relationships: bool = False,
        include_synonyms: bool = False,
        include_hierarchy: bool = False,
        vocab_release: str | None = None,
    ) -> Concept:
        """Get a concept by vocabulary and code.

        Args:
            vocabulary_id: The vocabulary ID (e.g., "SNOMED", "ICD10CM")
            concept_code: The concept code within the vocabulary
            include_relationships: Include related concepts (parents/children)
            include_synonyms: Include concept synonyms
            include_hierarchy: Include hierarchy information
            vocab_release: Specific vocabulary release (e.g., "2025.2")

        Returns:
            The concept data with optional relationships and synonyms
        """
        params: dict[str, Any] = {}
        if include_relationships:
            params["include_relationships"] = "true"
        if include_synonyms:
            params["include_synonyms"] = "true"
        if include_hierarchy:
            params["include_hierarchy"] = "true"
        if vocab_release:
            params["vocab_release"] = vocab_release

        return await self._request.get(
            f"/concepts/by-code/{vocabulary_id}/{concept_code}",
            params=params or None,
        )

    async def batch(
        self,
        concept_ids: list[int],
        *,
        include_relationships: bool = False,
        include_synonyms: bool = False,
        include_mappings: bool = False,
        vocabulary_filter: list[str] | None = None,
        standard_only: bool = True,
    ) -> BatchConceptResult:
        """Get multiple concepts by IDs (max 100)."""
        body: dict[str, Any] = {"concept_ids": concept_ids}
        if include_relationships:
            body["include_relationships"] = True
        if include_synonyms:
            body["include_synonyms"] = True
        if include_mappings:
            body["include_mappings"] = True
        if vocabulary_filter:
            body["vocabulary_filter"] = vocabulary_filter
        if standard_only:
            body["standard_only"] = True

        return await self._request.post("/concepts/batch", json_data=body)

    async def suggest(
        self,
        query: str,
        *,
        page: int = 1,
        page_size: int = 10,
        vocabulary_ids: list[str] | None = None,
        domain_ids: list[str] | None = None,
        vocab_release: str | None = None,
    ) -> dict[str, Any]:
        """Get concept suggestions (autocomplete).

        Args:
            query: Search query (min 2 characters, max 100 characters)
            page: Page number (default 1)
            page_size: Number of suggestions per page (default 10, max 100)
            vocabulary_ids: Filter to specific vocabularies (e.g., ["SNOMED", "ICD10CM"])
            domain_ids: Filter to specific domains (e.g., ["Condition", "Drug"])
            vocab_release: Specific vocabulary release (e.g., "2025.2")

        Returns:
            Paginated response with suggestions and pagination metadata
        """
        params: dict[str, Any] = {"query": query, "page": page, "page_size": page_size}
        if vocabulary_ids:
            params["vocabulary_ids"] = ",".join(vocabulary_ids)
        if domain_ids:
            params["domain_ids"] = ",".join(domain_ids)
        if vocab_release:
            params["vocab_release"] = vocab_release

        return await self._request.get("/concepts/suggest", params=params)

    async def related(
        self,
        concept_id: int,
        *,
        relationship_types: list[str] | None = None,
        min_score: float | None = None,
        page_size: int = 20,
        vocab_release: str | None = None,
    ) -> dict[str, Any]:
        """Get related concepts.

        Args:
            concept_id: The source concept ID
            relationship_types: Filter by relationship types (e.g., ["Is a", "Maps to"])
            min_score: Minimum relationship score (0.0-1.0)
            page_size: Maximum number of results (default 20, max 100)
            vocab_release: Specific vocabulary release (e.g., "2025.1")

        Returns:
            Related concepts with relationship scores
        """
        params: dict[str, Any] = {"page_size": page_size}
        if relationship_types:
            params["relationship_types"] = ",".join(relationship_types)
        if min_score is not None:
            params["min_score"] = min_score
        if vocab_release:
            params["vocab_release"] = vocab_release

        return await self._request.get(f"/concepts/{concept_id}/related", params=params)

    async def relationships(
        self,
        concept_id: int,
        *,
        relationship_ids: str | list[str] | None = None,
        vocabulary_ids: str | list[str] | None = None,
        domain_ids: str | list[str] | None = None,
        include_invalid: bool = False,
        standard_only: bool = False,
        include_reverse: bool = False,
        vocab_release: str | None = None,
    ) -> dict[str, Any]:
        """Get concept relationships."""
        params: dict[str, Any] = {}
        if relationship_ids:
            params["relationship_ids"] = (
                ",".join(relationship_ids)
                if isinstance(relationship_ids, list)
                else relationship_ids
            )
        if vocabulary_ids:
            params["vocabulary_ids"] = (
                ",".join(vocabulary_ids)
                if isinstance(vocabulary_ids, list)
                else vocabulary_ids
            )
        if domain_ids:
            params["domain_ids"] = (
                ",".join(domain_ids) if isinstance(domain_ids, list) else domain_ids
            )
        if include_invalid:
            params["include_invalid"] = "true"
        if standard_only:
            params["standard_only"] = "true"
        if include_reverse:
            params["include_reverse"] = "true"
        if vocab_release:
            params["vocab_release"] = vocab_release

        return await self._request.get(
            f"/concepts/{concept_id}/relationships", params=params
        )

    async def recommended(
        self,
        concept_ids: list[int],
        *,
        relationship_types: list[str] | None = None,
        vocabulary_ids: list[str] | None = None,
        domain_ids: list[str] | None = None,
        standard_only: bool = True,
        include_invalid: bool = False,
        page: int = 1,
        page_size: int = 100,
    ) -> dict[str, Any]:
        """Get recommended concepts using OHDSI Phoebe algorithm.

        Args:
            concept_ids: List of source concept IDs (1-100)
            relationship_types: Filter by relationship types (max 20)
            vocabulary_ids: Filter to specific vocabularies (max 50)
            domain_ids: Filter to specific domains (max 50)
            standard_only: Only return standard concepts (default True)
            include_invalid: Include invalid/deprecated concepts (default False)
            page: Page number (default 1)
            page_size: Results per page (default 100, max 1000)

        Returns:
            Recommendations grouped by source concept ID with pagination metadata
        """
        body: dict[str, Any] = {"concept_ids": concept_ids}
        if relationship_types:
            body["relationship_types"] = relationship_types
        if vocabulary_ids:
            body["vocabulary_ids"] = vocabulary_ids
        if domain_ids:
            body["domain_ids"] = domain_ids
        body["standard_only"] = standard_only
        body["include_invalid"] = include_invalid
        body["page"] = page
        body["page_size"] = page_size

        return await self._request.post("/concepts/recommended", json_data=body)
