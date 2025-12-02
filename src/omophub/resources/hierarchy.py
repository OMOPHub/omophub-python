"""Hierarchy resource implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .._request import AsyncRequest, Request


class Hierarchy:
    """Synchronous hierarchy resource."""

    def __init__(self, request: Request[Any]) -> None:
        self._request = request

    def ancestors(
        self,
        concept_id: int,
        *,
        vocabulary_id: str | None = None,
        max_levels: int | None = None,
        relationship_types: list[str] | None = None,
        include_paths: bool = False,
        include_distance: bool = True,
        standard_only: bool = False,
        include_deprecated: bool = False,
        page: int = 1,
        page_size: int = 100,
    ) -> dict[str, Any]:
        """Get concept ancestors.

        Args:
            concept_id: The concept ID
            vocabulary_id: Filter to specific vocabulary
            max_levels: Maximum hierarchy levels to traverse
            relationship_types: Relationship types to follow (default: "Is a")
            include_paths: Include path information
            include_distance: Include distance from source
            standard_only: Only return standard concepts
            include_deprecated: Include deprecated concepts
            page: Page number
            page_size: Results per page

        Returns:
            Ancestors with hierarchy summary
        """
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if vocabulary_id:
            params["vocabulary_id"] = vocabulary_id
        if max_levels is not None:
            params["max_levels"] = max_levels
        if relationship_types:
            params["relationship_types"] = ",".join(relationship_types)
        if include_paths:
            params["include_paths"] = "true"
        if include_distance:
            params["include_distance"] = "true"
        if standard_only:
            params["standard_only"] = "true"
        if include_deprecated:
            params["include_deprecated"] = "true"

        return self._request.get(f"/concepts/{concept_id}/ancestors", params=params)

    def descendants(
        self,
        concept_id: int,
        *,
        vocabulary_id: str | None = None,
        max_levels: int = 10,
        relationship_types: list[str] | None = None,
        include_distance: bool = True,
        standard_only: bool = False,
        include_deprecated: bool = False,
        domain_ids: list[str] | None = None,
        concept_class_ids: list[str] | None = None,
        include_synonyms: bool = False,
        page: int = 1,
        page_size: int = 100,
    ) -> dict[str, Any]:
        """Get concept descendants.

        Args:
            concept_id: The concept ID
            vocabulary_id: Filter to specific vocabulary
            max_levels: Maximum hierarchy levels (default 10, max 10)
            relationship_types: Relationship types to follow
            include_distance: Include distance from source
            standard_only: Only return standard concepts
            include_deprecated: Include deprecated concepts
            domain_ids: Filter by domains
            concept_class_ids: Filter by concept classes
            include_synonyms: Include synonyms
            page: Page number
            page_size: Results per page

        Returns:
            Descendants with hierarchy summary
        """
        params: dict[str, Any] = {
            "max_levels": min(max_levels, 10),
            "page": page,
            "page_size": page_size,
        }
        if vocabulary_id:
            params["vocabulary_id"] = vocabulary_id
        if relationship_types:
            params["relationship_types"] = ",".join(relationship_types)
        if include_distance:
            params["include_distance"] = "true"
        if standard_only:
            params["standard_only"] = "true"
        if include_deprecated:
            params["include_deprecated"] = "true"
        if domain_ids:
            params["domain_ids"] = ",".join(domain_ids)
        if concept_class_ids:
            params["concept_class_ids"] = ",".join(concept_class_ids)
        if include_synonyms:
            params["include_synonyms"] = "true"

        return self._request.get(f"/concepts/{concept_id}/descendants", params=params)


class AsyncHierarchy:
    """Asynchronous hierarchy resource."""

    def __init__(self, request: AsyncRequest[Any]) -> None:
        self._request = request

    async def ancestors(
        self,
        concept_id: int,
        *,
        vocabulary_id: str | None = None,
        max_levels: int | None = None,
        relationship_types: list[str] | None = None,
        include_paths: bool = False,
        include_distance: bool = True,
        standard_only: bool = False,
        include_deprecated: bool = False,
        page: int = 1,
        page_size: int = 100,
    ) -> dict[str, Any]:
        """Get concept ancestors."""
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if vocabulary_id:
            params["vocabulary_id"] = vocabulary_id
        if max_levels is not None:
            params["max_levels"] = max_levels
        if relationship_types:
            params["relationship_types"] = ",".join(relationship_types)
        if include_paths:
            params["include_paths"] = "true"
        if include_distance:
            params["include_distance"] = "true"
        if standard_only:
            params["standard_only"] = "true"
        if include_deprecated:
            params["include_deprecated"] = "true"

        return await self._request.get(
            f"/concepts/{concept_id}/ancestors", params=params
        )

    async def descendants(
        self,
        concept_id: int,
        *,
        vocabulary_id: str | None = None,
        max_levels: int = 10,
        relationship_types: list[str] | None = None,
        include_distance: bool = True,
        standard_only: bool = False,
        include_deprecated: bool = False,
        domain_ids: list[str] | None = None,
        concept_class_ids: list[str] | None = None,
        include_synonyms: bool = False,
        page: int = 1,
        page_size: int = 100,
    ) -> dict[str, Any]:
        """Get concept descendants."""
        params: dict[str, Any] = {
            "max_levels": min(max_levels, 10),
            "page": page,
            "page_size": page_size,
        }
        if vocabulary_id:
            params["vocabulary_id"] = vocabulary_id
        if relationship_types:
            params["relationship_types"] = ",".join(relationship_types)
        if include_distance:
            params["include_distance"] = "true"
        if standard_only:
            params["standard_only"] = "true"
        if include_deprecated:
            params["include_deprecated"] = "true"
        if domain_ids:
            params["domain_ids"] = ",".join(domain_ids)
        if concept_class_ids:
            params["concept_class_ids"] = ",".join(concept_class_ids)
        if include_synonyms:
            params["include_synonyms"] = "true"

        return await self._request.get(
            f"/concepts/{concept_id}/descendants", params=params
        )
