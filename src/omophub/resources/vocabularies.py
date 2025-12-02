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
        page_size: int = 100,
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

    def get(
        self,
        vocabulary_id: str,
        *,
        include_stats: bool = False,
        include_domains: bool = False,
    ) -> Vocabulary:
        """Get vocabulary details.

        Args:
            vocabulary_id: The vocabulary ID
            include_stats: Include statistics
            include_domains: Include domain breakdown

        Returns:
            Vocabulary details
        """
        params: dict[str, Any] = {}
        if include_stats:
            params["include_stats"] = "true"
        if include_domains:
            params["include_domains"] = "true"

        return self._request.get(
            f"/vocabularies/{vocabulary_id}", params=params or None
        )

    def stats(self, vocabulary_id: str) -> VocabularyStats:
        """Get vocabulary statistics.

        Args:
            vocabulary_id: The vocabulary ID

        Returns:
            Vocabulary statistics
        """
        return self._request.get(f"/vocabularies/{vocabulary_id}/stats")

    def domains(
        self,
        *,
        vocabulary_ids: list[str] | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> dict[str, Any]:
        """Get vocabulary domains.

        Args:
            vocabulary_ids: Filter by vocabulary IDs (optional)
            page: Page number
            page_size: Results per page

        Returns:
            Domain statistics for vocabularies
        """
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if vocabulary_ids:
            params["vocabulary_ids"] = ",".join(vocabulary_ids)
        return self._request.get("/vocabularies/domains", params=params)

    def concepts(
        self,
        vocabulary_id: str,
        *,
        domain_id: str | None = None,
        concept_class_id: str | None = None,
        standard_only: bool = False,
        page: int = 1,
        page_size: int = 50,
    ) -> dict[str, Any]:
        """Get concepts in a vocabulary.

        Args:
            vocabulary_id: The vocabulary ID
            domain_id: Filter by domain
            concept_class_id: Filter by concept class
            standard_only: Only standard concepts
            page: Page number
            page_size: Results per page

        Returns:
            Paginated concepts
        """
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if domain_id:
            params["domain_id"] = domain_id
        if concept_class_id:
            params["concept_class_id"] = concept_class_id
        if standard_only:
            params["standard_only"] = "true"

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
        page_size: int = 100,
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

    async def get(
        self,
        vocabulary_id: str,
        *,
        include_stats: bool = False,
        include_domains: bool = False,
    ) -> Vocabulary:
        """Get vocabulary details."""
        params: dict[str, Any] = {}
        if include_stats:
            params["include_stats"] = "true"
        if include_domains:
            params["include_domains"] = "true"

        return await self._request.get(
            f"/vocabularies/{vocabulary_id}", params=params or None
        )

    async def stats(self, vocabulary_id: str) -> VocabularyStats:
        """Get vocabulary statistics."""
        return await self._request.get(f"/vocabularies/{vocabulary_id}/stats")

    async def domains(
        self,
        *,
        vocabulary_ids: list[str] | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> dict[str, Any]:
        """Get vocabulary domains."""
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if vocabulary_ids:
            params["vocabulary_ids"] = ",".join(vocabulary_ids)
        return await self._request.get("/vocabularies/domains", params=params)

    async def concepts(
        self,
        vocabulary_id: str,
        *,
        domain_id: str | None = None,
        concept_class_id: str | None = None,
        standard_only: bool = False,
        page: int = 1,
        page_size: int = 50,
    ) -> dict[str, Any]:
        """Get concepts in a vocabulary."""
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if domain_id:
            params["domain_id"] = domain_id
        if concept_class_id:
            params["concept_class_id"] = concept_class_id
        if standard_only:
            params["standard_only"] = "true"

        return await self._request.get(
            f"/vocabularies/{vocabulary_id}/concepts", params=params
        )
