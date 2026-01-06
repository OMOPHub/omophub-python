"""Hierarchy resource implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .._request import AsyncRequest, Request


class Hierarchy:
    """Synchronous hierarchy resource."""

    def __init__(self, request: Request[Any]) -> None:
        self._request = request

    def get(
        self,
        concept_id: int,
        *,
        format: str = "flat",
        vocabulary_ids: list[str] | None = None,
        domain_ids: list[str] | None = None,
        max_levels: int = 10,
        max_results: int | None = None,
        relationship_types: list[str] | None = None,
        include_invalid: bool = False,
    ) -> dict[str, Any]:
        """Get complete concept hierarchy (ancestors and descendants).

        Args:
            concept_id: The concept ID
            format: Response format - "flat" (default) or "graph" for visualization
            vocabulary_ids: Filter to specific vocabularies (e.g., ["SNOMED", "ICD10CM"])
            domain_ids: Filter to specific domains (e.g., ["Condition", "Drug"])
            max_levels: Maximum hierarchy levels to traverse in both directions (default 10)
            max_results: Maximum results per direction for performance optimization
            relationship_types: Relationship types to follow (default: "Is a")
            include_invalid: Include deprecated/invalid concepts (default: False)

        Returns:
            For flat format: ancestors, descendants arrays with level/total counts
            For graph format: nodes and edges arrays for visualization
        """
        params: dict[str, Any] = {
            "format": format,
            "max_levels": min(max_levels, 20),
        }
        if vocabulary_ids:
            params["vocabulary_ids"] = ",".join(vocabulary_ids)
        if domain_ids:
            params["domain_ids"] = ",".join(domain_ids)
        if max_results is not None:
            params["max_results"] = max_results
        if relationship_types:
            params["relationship_types"] = ",".join(relationship_types)
        if include_invalid:
            params["include_invalid"] = "true"

        return self._request.get(f"/concepts/{concept_id}/hierarchy", params=params)

    def ancestors(
        self,
        concept_id: int,
        *,
        vocabulary_ids: list[str] | None = None,
        max_levels: int | None = None,
        relationship_types: list[str] | None = None,
        include_paths: bool = False,
        include_distance: bool = True,
        include_invalid: bool = False,
        page: int = 1,
        page_size: int = 100,
    ) -> dict[str, Any]:
        """Get concept ancestors.

        Args:
            concept_id: The concept ID
            vocabulary_ids: Filter to specific vocabularies (e.g., ["SNOMED", "ICD10CM"])
            max_levels: Maximum hierarchy levels to traverse
            relationship_types: Relationship types to follow (default: "Is a")
            include_paths: Include path_length field for each ancestor
            include_distance: Include hierarchy_level field for each ancestor
            include_invalid: Include deprecated/invalid concepts (default: False)
            page: Page number
            page_size: Results per page

        Returns:
            Ancestors with hierarchy_summary and pagination metadata
        """
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if vocabulary_ids:
            params["vocabulary_ids"] = ",".join(vocabulary_ids)
        if max_levels is not None:
            params["max_levels"] = max_levels
        if relationship_types:
            params["relationship_types"] = ",".join(relationship_types)
        if include_paths:
            params["include_paths"] = "true"
        if include_distance:
            params["include_distance"] = "true"
        if include_invalid:
            params["include_invalid"] = "true"

        return self._request.get(f"/concepts/{concept_id}/ancestors", params=params)

    def descendants(
        self,
        concept_id: int,
        *,
        vocabulary_ids: list[str] | None = None,
        max_levels: int = 10,
        relationship_types: list[str] | None = None,
        include_distance: bool = True,
        include_paths: bool = False,
        include_invalid: bool = False,
        domain_ids: list[str] | None = None,
        page: int = 1,
        page_size: int = 100,
    ) -> dict[str, Any]:
        """Get concept descendants.

        Args:
            concept_id: The concept ID
            vocabulary_ids: Filter to specific vocabularies (e.g., ["SNOMED", "ICD10CM"])
            max_levels: Maximum hierarchy levels (default 10, max 20)
            relationship_types: Relationship types to follow (default: "Is a")
            include_distance: Include hierarchy_level field for each descendant
            include_paths: Include path_length field for each descendant
            include_invalid: Include deprecated/invalid concepts (default: False)
            domain_ids: Filter by domains (e.g., ["Condition", "Drug"])
            page: Page number
            page_size: Results per page

        Returns:
            Descendants with hierarchy_summary and pagination metadata
        """
        params: dict[str, Any] = {
            "max_levels": min(max_levels, 20),
            "page": page,
            "page_size": page_size,
        }
        if vocabulary_ids:
            params["vocabulary_ids"] = ",".join(vocabulary_ids)
        if relationship_types:
            params["relationship_types"] = ",".join(relationship_types)
        if include_distance:
            params["include_distance"] = "true"
        if include_paths:
            params["include_paths"] = "true"
        if include_invalid:
            params["include_invalid"] = "true"
        if domain_ids:
            params["domain_ids"] = ",".join(domain_ids)

        return self._request.get(f"/concepts/{concept_id}/descendants", params=params)


class AsyncHierarchy:
    """Asynchronous hierarchy resource."""

    def __init__(self, request: AsyncRequest[Any]) -> None:
        self._request = request

    async def get(
        self,
        concept_id: int,
        *,
        format: str = "flat",
        vocabulary_ids: list[str] | None = None,
        domain_ids: list[str] | None = None,
        max_levels: int = 10,
        max_results: int | None = None,
        relationship_types: list[str] | None = None,
        include_invalid: bool = False,
    ) -> dict[str, Any]:
        """Get complete concept hierarchy (ancestors and descendants)."""
        params: dict[str, Any] = {
            "format": format,
            "max_levels": min(max_levels, 20),
        }
        if vocabulary_ids:
            params["vocabulary_ids"] = ",".join(vocabulary_ids)
        if domain_ids:
            params["domain_ids"] = ",".join(domain_ids)
        if max_results is not None:
            params["max_results"] = max_results
        if relationship_types:
            params["relationship_types"] = ",".join(relationship_types)
        if include_invalid:
            params["include_invalid"] = "true"

        return await self._request.get(
            f"/concepts/{concept_id}/hierarchy", params=params
        )

    async def ancestors(
        self,
        concept_id: int,
        *,
        vocabulary_ids: list[str] | None = None,
        max_levels: int | None = None,
        relationship_types: list[str] | None = None,
        include_paths: bool = False,
        include_distance: bool = True,
        include_invalid: bool = False,
        page: int = 1,
        page_size: int = 100,
    ) -> dict[str, Any]:
        """Get concept ancestors."""
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if vocabulary_ids:
            params["vocabulary_ids"] = ",".join(vocabulary_ids)
        if max_levels is not None:
            params["max_levels"] = max_levels
        if relationship_types:
            params["relationship_types"] = ",".join(relationship_types)
        if include_paths:
            params["include_paths"] = "true"
        if include_distance:
            params["include_distance"] = "true"
        if include_invalid:
            params["include_invalid"] = "true"

        return await self._request.get(
            f"/concepts/{concept_id}/ancestors", params=params
        )

    async def descendants(
        self,
        concept_id: int,
        *,
        vocabulary_ids: list[str] | None = None,
        max_levels: int = 10,
        relationship_types: list[str] | None = None,
        include_distance: bool = True,
        include_paths: bool = False,
        include_invalid: bool = False,
        domain_ids: list[str] | None = None,
        page: int = 1,
        page_size: int = 100,
    ) -> dict[str, Any]:
        """Get concept descendants."""
        params: dict[str, Any] = {
            "max_levels": min(max_levels, 20),
            "page": page,
            "page_size": page_size,
        }
        if vocabulary_ids:
            params["vocabulary_ids"] = ",".join(vocabulary_ids)
        if relationship_types:
            params["relationship_types"] = ",".join(relationship_types)
        if include_distance:
            params["include_distance"] = "true"
        if include_paths:
            params["include_paths"] = "true"
        if include_invalid:
            params["include_invalid"] = "true"
        if domain_ids:
            params["domain_ids"] = ",".join(domain_ids)

        return await self._request.get(
            f"/concepts/{concept_id}/descendants", params=params
        )
