"""Vocabularies resource implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .._request import AsyncRequest, Request
    from ..types.vocabulary import Vocabulary, VocabularyStats


class Vocabularies:
    """Synchronous vocabularies resource."""

    def __init__(self, request: Request[Any]) -> None:
        self._request = request

    def list(
        self,
        *,
        include_stats: bool = False,
        include_inactive: bool = False,
        sort_by: str = "name",
        sort_order: str = "asc",
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """List all vocabularies.

        Args:
            include_stats: Include vocabulary statistics
            include_inactive: Include inactive vocabularies
            sort_by: Sort field ("name", "priority", "updated")
            sort_order: Sort order ("asc" or "desc")
            page: Page number
            page_size: Results per page

        Returns:
            Paginated vocabulary list
        """
        params: dict[str, Any] = {
            "sort_by": sort_by,
            "sort_order": sort_order,
            "page": page,
            "page_size": page_size,
        }
        if include_stats:
            params["include_stats"] = "true"
        if include_inactive:
            params["include_inactive"] = "true"

        return self._request.get("/vocabularies", params=params)

    def get(self, vocabulary_id: str) -> Vocabulary:
        """Get vocabulary details.

        Args:
            vocabulary_id: The vocabulary ID

        Returns:
            Vocabulary details including vocabulary_id, vocabulary_name,
            vocabulary_reference, vocabulary_version, vocabulary_concept_id
        """
        return self._request.get(f"/vocabularies/{vocabulary_id}")

    def stats(self, vocabulary_id: str) -> VocabularyStats:
        """Get vocabulary statistics.

        Args:
            vocabulary_id: The vocabulary ID

        Returns:
            Vocabulary statistics
        """
        return self._request.get(f"/vocabularies/{vocabulary_id}/stats")

    def domain_stats(self, vocabulary_id: str, domain_id: str) -> dict[str, Any]:
        """Get statistics for a specific domain within a vocabulary.

        Args:
            vocabulary_id: The vocabulary ID (e.g., "SNOMED", "ICD10CM")
            domain_id: The domain ID (e.g., "Condition", "Drug", "Procedure")

        Returns:
            Domain statistics including concept counts and class breakdown
        """
        return self._request.get(
            f"/vocabularies/{vocabulary_id}/stats/domains/{domain_id}"
        )

    def domains(self) -> dict[str, Any]:
        """Get all standard OHDSI domains.

        Returns:
            List of all available domains with domain_id, domain_name, and description
        """
        return self._request.get("/vocabularies/domains")

    def concept_classes(self) -> dict[str, Any]:
        """Get all concept classes.

        Returns:
            List of all available concept classes with concept_class_id,
            concept_class_name, and concept_class_concept_id
        """
        return self._request.get("/vocabularies/concept-classes")

    def concepts(
        self,
        vocabulary_id: str,
        *,
        search: str | None = None,
        standard_concept: str = "all",
        include_invalid: bool = False,
        include_relationships: bool = False,
        include_synonyms: bool = False,
        sort_by: str = "name",
        sort_order: str = "asc",
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """Get concepts in a vocabulary.

        Args:
            vocabulary_id: The vocabulary ID
            search: Search term to filter concepts by name or code
            standard_concept: Filter by standard concept status ('S', 'C', 'all')
            include_invalid: Include invalid or deprecated concepts
            include_relationships: Include concept relationships
            include_synonyms: Include concept synonyms
            sort_by: Sort field ('name', 'concept_id', 'concept_code')
            sort_order: Sort order ('asc' or 'desc')
            page: Page number
            page_size: Results per page (max 1000)

        Returns:
            Paginated concepts
        """
        params: dict[str, Any] = {
            "page": page,
            "page_size": page_size,
            "standard_concept": standard_concept,
            "sort_by": sort_by,
            "sort_order": sort_order,
        }
        if search:
            params["search"] = search
        if include_invalid:
            params["include_invalid"] = "true"
        if include_relationships:
            params["include_relationships"] = "true"
        if include_synonyms:
            params["include_synonyms"] = "true"

        return self._request.get(
            f"/vocabularies/{vocabulary_id}/concepts", params=params
        )


class AsyncVocabularies:
    """Asynchronous vocabularies resource."""

    def __init__(self, request: AsyncRequest[Any]) -> None:
        self._request = request

    async def list(
        self,
        *,
        include_stats: bool = False,
        include_inactive: bool = False,
        sort_by: str = "name",
        sort_order: str = "asc",
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """List all vocabularies."""
        params: dict[str, Any] = {
            "sort_by": sort_by,
            "sort_order": sort_order,
            "page": page,
            "page_size": page_size,
        }
        if include_stats:
            params["include_stats"] = "true"
        if include_inactive:
            params["include_inactive"] = "true"

        return await self._request.get("/vocabularies", params=params)

    async def get(self, vocabulary_id: str) -> Vocabulary:
        """Get vocabulary details."""
        return await self._request.get(f"/vocabularies/{vocabulary_id}")

    async def stats(self, vocabulary_id: str) -> VocabularyStats:
        """Get vocabulary statistics."""
        return await self._request.get(f"/vocabularies/{vocabulary_id}/stats")

    async def domain_stats(self, vocabulary_id: str, domain_id: str) -> dict[str, Any]:
        """Get statistics for a specific domain within a vocabulary."""
        return await self._request.get(
            f"/vocabularies/{vocabulary_id}/stats/domains/{domain_id}"
        )

    async def domains(self) -> dict[str, Any]:
        """Get all standard OHDSI domains."""
        return await self._request.get("/vocabularies/domains")

    async def concept_classes(self) -> dict[str, Any]:
        """Get all concept classes."""
        return await self._request.get("/vocabularies/concept-classes")

    async def concepts(
        self,
        vocabulary_id: str,
        *,
        search: str | None = None,
        standard_concept: str = "all",
        include_invalid: bool = False,
        include_relationships: bool = False,
        include_synonyms: bool = False,
        sort_by: str = "name",
        sort_order: str = "asc",
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """Get concepts in a vocabulary."""
        params: dict[str, Any] = {
            "page": page,
            "page_size": page_size,
            "standard_concept": standard_concept,
            "sort_by": sort_by,
            "sort_order": sort_order,
        }
        if search:
            params["search"] = search
        if include_invalid:
            params["include_invalid"] = "true"
        if include_relationships:
            params["include_relationships"] = "true"
        if include_synonyms:
            params["include_synonyms"] = "true"

        return await self._request.get(
            f"/vocabularies/{vocabulary_id}/concepts", params=params
        )
