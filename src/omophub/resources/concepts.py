"""Concepts resource implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypedDict

if TYPE_CHECKING:
    from .._request import AsyncRequest, Request
    from ..types.concept import BatchConceptResult, Concept
    from ..types.search import Suggestion


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
    vocabulary: str
    domain: str
    limit: int


class RelatedParams(TypedDict, total=False):
    """Parameters for related concepts."""

    relatedness_types: list[str]
    vocabulary_ids: list[str]
    domain_ids: list[str]
    min_relatedness_score: float
    max_results: int
    include_scores: bool
    standard_concepts_only: bool


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
    ) -> Concept:
        """Get a concept by ID.

        Args:
            concept_id: The OMOP concept ID
            include_relationships: Include related concepts
            include_synonyms: Include concept synonyms

        Returns:
            The concept data
        """
        params: dict[str, Any] = {}
        if include_relationships:
            params["include_relationships"] = "true"
        if include_synonyms:
            params["include_synonyms"] = "true"

        return self._request.get(f"/concepts/{concept_id}", params=params or None)

    def get_by_code(
        self,
        vocabulary_id: str,
        concept_code: str,
    ) -> Concept:
        """Get a concept by vocabulary and code.

        Args:
            vocabulary_id: The vocabulary ID (e.g., "SNOMED", "ICD10CM")
            concept_code: The concept code within the vocabulary

        Returns:
            The concept data with mappings
        """
        return self._request.get(f"/concepts/by-code/{vocabulary_id}/{concept_code}")

    def batch(
        self,
        concept_ids: list[int],
        *,
        include_relationships: bool = False,
        include_synonyms: bool = False,
        include_mappings: bool = False,
        vocabulary_filter: list[str] | None = None,
        standard_only: bool = False,
    ) -> BatchConceptResult:
        """Get multiple concepts by IDs.

        Args:
            concept_ids: List of concept IDs (max 1000)
            include_relationships: Include related concepts
            include_synonyms: Include concept synonyms
            include_mappings: Include concept mappings
            vocabulary_filter: Filter results to specific vocabularies
            standard_only: Only return standard concepts

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
        vocabulary: str | None = None,
        domain: str | None = None,
        limit: int = 10,
    ) -> list[Suggestion]:
        """Get concept suggestions (autocomplete).

        Args:
            query: Search query (min 2 characters)
            vocabulary: Filter to specific vocabulary
            domain: Filter to specific domain
            limit: Maximum suggestions (default 10, max 50)

        Returns:
            List of suggestions
        """
        params: dict[str, Any] = {"query": query, "limit": limit}
        if vocabulary:
            params["vocabulary"] = vocabulary
        if domain:
            params["domain"] = domain

        return self._request.get("/concepts/suggest", params=params)

    def related(
        self,
        concept_id: int,
        *,
        relatedness_types: list[str] | None = None,
        vocabulary_ids: list[str] | None = None,
        domain_ids: list[str] | None = None,
        min_relatedness_score: float | None = None,
        max_results: int = 50,
        include_scores: bool = True,
        standard_concepts_only: bool = False,
    ) -> dict[str, Any]:
        """Get related concepts.

        Args:
            concept_id: The source concept ID
            relatedness_types: Types of relatedness (hierarchical, semantic, etc.)
            vocabulary_ids: Filter to specific vocabularies
            domain_ids: Filter to specific domains
            min_relatedness_score: Minimum relatedness score
            max_results: Maximum results (default 50, max 200)
            include_scores: Include score breakdown
            standard_concepts_only: Only return standard concepts

        Returns:
            Related concepts with scores and analysis
        """
        params: dict[str, Any] = {
            "max_results": max_results,
            "include_scores": "true" if include_scores else "false",
        }
        if relatedness_types:
            params["relatedness_types"] = ",".join(relatedness_types)
        if vocabulary_ids:
            params["vocabulary_ids"] = ",".join(vocabulary_ids)
        if domain_ids:
            params["domain_ids"] = ",".join(domain_ids)
        if min_relatedness_score is not None:
            params["min_relatedness_score"] = min_relatedness_score
        if standard_concepts_only:
            params["standard_concepts_only"] = "true"

        return self._request.get(f"/concepts/{concept_id}/related", params=params)

    def relationships(
        self,
        concept_id: int,
        *,
        relationship_type: str | None = None,
        target_vocabulary: str | None = None,
        include_invalid: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """Get concept relationships.

        Args:
            concept_id: The concept ID
            relationship_type: Filter by relationship type
            target_vocabulary: Filter by target vocabulary
            include_invalid: Include invalid relationships
            page: Page number
            page_size: Items per page

        Returns:
            Relationships with summary
        """
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if relationship_type:
            params["relationship_type"] = relationship_type
        if target_vocabulary:
            params["target_vocabulary"] = target_vocabulary
        if include_invalid:
            params["include_invalid"] = "true"

        return self._request.get(f"/concepts/{concept_id}/relationships", params=params)


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
    ) -> Concept:
        """Get a concept by ID."""
        params: dict[str, Any] = {}
        if include_relationships:
            params["include_relationships"] = "true"
        if include_synonyms:
            params["include_synonyms"] = "true"

        return await self._request.get(f"/concepts/{concept_id}", params=params or None)

    async def get_by_code(
        self,
        vocabulary_id: str,
        concept_code: str,
    ) -> Concept:
        """Get a concept by vocabulary and code."""
        return await self._request.get(
            f"/concepts/by-code/{vocabulary_id}/{concept_code}"
        )

    async def batch(
        self,
        concept_ids: list[int],
        *,
        include_relationships: bool = False,
        include_synonyms: bool = False,
        include_mappings: bool = False,
        vocabulary_filter: list[str] | None = None,
        standard_only: bool = False,
    ) -> BatchConceptResult:
        """Get multiple concepts by IDs."""
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
        vocabulary: str | None = None,
        domain: str | None = None,
        limit: int = 10,
    ) -> list[Suggestion]:
        """Get concept suggestions (autocomplete)."""
        params: dict[str, Any] = {"query": query, "limit": limit}
        if vocabulary:
            params["vocabulary"] = vocabulary
        if domain:
            params["domain"] = domain

        return await self._request.get("/concepts/suggest", params=params)

    async def related(
        self,
        concept_id: int,
        *,
        relatedness_types: list[str] | None = None,
        vocabulary_ids: list[str] | None = None,
        domain_ids: list[str] | None = None,
        min_relatedness_score: float | None = None,
        max_results: int = 50,
        include_scores: bool = True,
        standard_concepts_only: bool = False,
    ) -> dict[str, Any]:
        """Get related concepts."""
        params: dict[str, Any] = {
            "max_results": max_results,
            "include_scores": "true" if include_scores else "false",
        }
        if relatedness_types:
            params["relatedness_types"] = ",".join(relatedness_types)
        if vocabulary_ids:
            params["vocabulary_ids"] = ",".join(vocabulary_ids)
        if domain_ids:
            params["domain_ids"] = ",".join(domain_ids)
        if min_relatedness_score is not None:
            params["min_relatedness_score"] = min_relatedness_score
        if standard_concepts_only:
            params["standard_concepts_only"] = "true"

        return await self._request.get(f"/concepts/{concept_id}/related", params=params)

    async def relationships(
        self,
        concept_id: int,
        *,
        relationship_type: str | None = None,
        target_vocabulary: str | None = None,
        include_invalid: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """Get concept relationships."""
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if relationship_type:
            params["relationship_type"] = relationship_type
        if target_vocabulary:
            params["target_vocabulary"] = target_vocabulary
        if include_invalid:
            params["include_invalid"] = "true"

        return await self._request.get(
            f"/concepts/{concept_id}/relationships", params=params
        )
