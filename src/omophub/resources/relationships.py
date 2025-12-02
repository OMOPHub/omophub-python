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
        relationship_type: str | None = None,
        target_vocabulary: str | None = None,
        include_invalid: bool = False,
        page: int = 1,
        page_size: int = 50,
    ) -> dict[str, Any]:
        """Get relationships for a concept.

        Args:
            concept_id: The concept ID
            relationship_type: Filter by relationship type
            target_vocabulary: Filter by target vocabulary
            include_invalid: Include invalid relationships
            page: Page number
            page_size: Results per page

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

    def types(
        self,
        *,
        vocabulary_ids: list[str] | None = None,
        include_reverse: bool = False,
        include_usage_stats: bool = False,
        include_examples: bool = False,
        category: str | None = None,
        is_defining: bool | None = None,
        standard_only: bool = False,
        page: int = 1,
        page_size: int = 100,
    ) -> dict[str, Any]:
        """Get available relationship types.

        Args:
            vocabulary_ids: Filter by vocabularies
            include_reverse: Include reverse relationships
            include_usage_stats: Include usage statistics
            include_examples: Include example concepts
            category: Filter by category
            is_defining: Filter by defining status
            standard_only: Only standard relationships
            page: Page number
            page_size: Results per page

        Returns:
            Relationship types with metadata
        """
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if vocabulary_ids:
            params["vocabulary_ids"] = ",".join(vocabulary_ids)
        if include_reverse:
            params["include_reverse"] = "true"
        if include_usage_stats:
            params["include_usage_stats"] = "true"
        if include_examples:
            params["include_examples"] = "true"
        if category:
            params["category"] = category
        if is_defining is not None:
            params["is_defining"] = "true" if is_defining else "false"
        if standard_only:
            params["standard_only"] = "true"

        return self._request.get("/relationships/types", params=params)


class AsyncRelationships:
    """Asynchronous relationships resource."""

    def __init__(self, request: AsyncRequest[Any]) -> None:
        self._request = request

    async def get(
        self,
        concept_id: int,
        *,
        relationship_type: str | None = None,
        target_vocabulary: str | None = None,
        include_invalid: bool = False,
        page: int = 1,
        page_size: int = 50,
    ) -> dict[str, Any]:
        """Get relationships for a concept.

        Args:
            concept_id: The concept ID
            relationship_type: Filter by relationship type
            target_vocabulary: Filter by target vocabulary
            include_invalid: Include invalid relationships
            page: Page number
            page_size: Results per page

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

        return await self._request.get(
            f"/concepts/{concept_id}/relationships", params=params
        )

    async def types(
        self,
        *,
        vocabulary_ids: list[str] | None = None,
        include_reverse: bool = False,
        include_usage_stats: bool = False,
        include_examples: bool = False,
        category: str | None = None,
        is_defining: bool | None = None,
        standard_only: bool = False,
        page: int = 1,
        page_size: int = 100,
    ) -> dict[str, Any]:
        """Get available relationship types.

        Args:
            vocabulary_ids: Filter by vocabularies
            include_reverse: Include reverse relationships
            include_usage_stats: Include usage statistics
            include_examples: Include example concepts
            category: Filter by category
            is_defining: Filter by defining status
            standard_only: Only standard relationships
            page: Page number
            page_size: Results per page

        Returns:
            Relationship types with metadata
        """
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if vocabulary_ids:
            params["vocabulary_ids"] = ",".join(vocabulary_ids)
        if include_reverse:
            params["include_reverse"] = "true"
        if include_usage_stats:
            params["include_usage_stats"] = "true"
        if include_examples:
            params["include_examples"] = "true"
        if category:
            params["category"] = category
        if is_defining is not None:
            params["is_defining"] = "true" if is_defining else "false"
        if standard_only:
            params["standard_only"] = "true"

        return await self._request.get("/relationships/types", params=params)
