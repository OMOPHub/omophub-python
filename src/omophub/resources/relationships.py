"""Relationships resource implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .._request import AsyncRequest, Request


class Relationships:
    """Synchronous relationships resource."""

    def __init__(self, request: Request[Any]) -> None:
        self._request = request

    def get(
        self,
        concept_id: int,
        *,
        relationship_ids: list[str] | None = None,
        vocabulary_ids: list[str] | None = None,
        domain_ids: list[str] | None = None,
        standard_only: bool = False,
        include_invalid: bool = False,
        include_reverse: bool = False,
        page: int = 1,
        page_size: int = 100,
    ) -> dict[str, Any]:
        """Get relationships for a concept.

        Args:
            concept_id: The concept ID
            relationship_ids: Filter by relationship IDs (e.g., ["Is a", "Maps to"])
            vocabulary_ids: Filter by vocabulary IDs
            domain_ids: Filter by domain IDs
            standard_only: Only include relationships to standard concepts
            include_invalid: Include invalid relationships
            include_reverse: Include reverse relationships
            page: Page number
            page_size: Results per page (max 1000)

        Returns:
            Relationships with pagination metadata
        """
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if relationship_ids:
            params["relationship_ids"] = ",".join(relationship_ids)
        if vocabulary_ids:
            params["vocabulary_ids"] = ",".join(vocabulary_ids)
        if domain_ids:
            params["domain_ids"] = ",".join(domain_ids)
        if standard_only:
            params["standard_only"] = "true"
        if include_invalid:
            params["include_invalid"] = "true"
        if include_reverse:
            params["include_reverse"] = "true"

        return self._request.get(f"/concepts/{concept_id}/relationships", params=params)

    def types(
        self,
        *,
        page: int = 1,
        page_size: int = 100,
    ) -> dict[str, Any]:
        """Get available relationship types from the OMOP CDM.

        Args:
            page: Page number (1-based)
            page_size: Results per page (max 500)

        Returns:
            Relationship types with pagination metadata
        """
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        return self._request.get("/relationships/types", params=params)


class AsyncRelationships:
    """Asynchronous relationships resource."""

    def __init__(self, request: AsyncRequest[Any]) -> None:
        self._request = request

    async def get(
        self,
        concept_id: int,
        *,
        relationship_ids: list[str] | None = None,
        vocabulary_ids: list[str] | None = None,
        domain_ids: list[str] | None = None,
        standard_only: bool = False,
        include_invalid: bool = False,
        include_reverse: bool = False,
        page: int = 1,
        page_size: int = 100,
    ) -> dict[str, Any]:
        """Get relationships for a concept.

        Args:
            concept_id: The concept ID
            relationship_ids: Filter by relationship IDs (e.g., ["Is a", "Maps to"])
            vocabulary_ids: Filter by vocabulary IDs
            domain_ids: Filter by domain IDs
            standard_only: Only include relationships to standard concepts
            include_invalid: Include invalid relationships
            include_reverse: Include reverse relationships
            page: Page number
            page_size: Results per page (max 1000)

        Returns:
            Relationships with pagination metadata
        """
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if relationship_ids:
            params["relationship_ids"] = ",".join(relationship_ids)
        if vocabulary_ids:
            params["vocabulary_ids"] = ",".join(vocabulary_ids)
        if domain_ids:
            params["domain_ids"] = ",".join(domain_ids)
        if standard_only:
            params["standard_only"] = "true"
        if include_invalid:
            params["include_invalid"] = "true"
        if include_reverse:
            params["include_reverse"] = "true"

        return await self._request.get(
            f"/concepts/{concept_id}/relationships", params=params
        )

    async def types(
        self,
        *,
        page: int = 1,
        page_size: int = 100,
    ) -> dict[str, Any]:
        """Get available relationship types from the OMOP CDM.

        Args:
            page: Page number (1-based)
            page_size: Results per page (max 500)

        Returns:
            Relationship types with pagination metadata
        """
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        return await self._request.get("/relationships/types", params=params)
