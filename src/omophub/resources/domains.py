"""Domains resource implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import builtins

    from .._request import AsyncRequest, Request


class Domains:
    """Synchronous domains resource."""

    def __init__(self, request: Request[Any]) -> None:
        self._request = request

    def list(
        self,
        *,
        vocabulary_ids: builtins.list[str] | None = None,
        include_concept_counts: bool = True,
        include_statistics: bool = False,
        include_examples: bool = False,
        standard_only: bool = False,
        active_only: bool = True,
        sort_by: str = "domain_id",
        sort_order: str = "asc",
    ) -> dict[str, Any]:
        """List all domains.

        Args:
            vocabulary_ids: Filter by vocabularies
            include_concept_counts: Include concept counts
            include_statistics: Include detailed statistics
            include_examples: Include example concepts
            standard_only: Only standard concepts
            active_only: Only active domains
            sort_by: Sort field
            sort_order: Sort order

        Returns:
            Domain list with summary
        """
        params: dict[str, Any] = {
            "sort_by": sort_by,
            "sort_order": sort_order,
        }
        if vocabulary_ids:
            params["vocabulary_ids"] = ",".join(vocabulary_ids)
        if include_concept_counts:
            params["include_concept_counts"] = "true"
        if include_statistics:
            params["include_statistics"] = "true"
        if include_examples:
            params["include_examples"] = "true"
        if standard_only:
            params["standard_only"] = "true"
        if not active_only:
            params["active_only"] = "false"

        return self._request.get("/domains", params=params)

    def concepts(
        self,
        domain_id: str,
        *,
        vocabulary_ids: builtins.list[str] | None = None,
        concept_class_ids: builtins.list[str] | None = None,
        standard_only: bool = False,
        page: int = 1,
        page_size: int = 50,
    ) -> dict[str, Any]:
        """Get concepts in a domain.

        Args:
            domain_id: The domain ID
            vocabulary_ids: Filter by vocabularies
            concept_class_ids: Filter by concept classes
            standard_only: Only standard concepts
            page: Page number
            page_size: Results per page

        Returns:
            Paginated concepts
        """
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if vocabulary_ids:
            params["vocabulary_ids"] = ",".join(vocabulary_ids)
        if concept_class_ids:
            params["concept_class_ids"] = ",".join(concept_class_ids)
        if standard_only:
            params["standard_only"] = "true"

        return self._request.get(f"/domains/{domain_id}/concepts", params=params)


class AsyncDomains:
    """Asynchronous domains resource."""

    def __init__(self, request: AsyncRequest[Any]) -> None:
        self._request = request

    async def list(
        self,
        *,
        vocabulary_ids: builtins.list[str] | None = None,
        include_concept_counts: bool = True,
        include_statistics: bool = False,
        include_examples: bool = False,
        standard_only: bool = False,
        active_only: bool = True,
        sort_by: str = "domain_id",
        sort_order: str = "asc",
    ) -> dict[str, Any]:
        """List all domains.

        Args:
            vocabulary_ids: Filter by vocabularies
            include_concept_counts: Include concept counts
            include_statistics: Include detailed statistics
            include_examples: Include example concepts
            standard_only: Only standard concepts
            active_only: Only active domains
            sort_by: Sort field
            sort_order: Sort order

        Returns:
            Domain list with summary
        """
        params: dict[str, Any] = {
            "sort_by": sort_by,
            "sort_order": sort_order,
        }
        if vocabulary_ids:
            params["vocabulary_ids"] = ",".join(vocabulary_ids)
        if include_concept_counts:
            params["include_concept_counts"] = "true"
        if include_statistics:
            params["include_statistics"] = "true"
        if include_examples:
            params["include_examples"] = "true"
        if standard_only:
            params["standard_only"] = "true"
        if not active_only:
            params["active_only"] = "false"

        return await self._request.get("/domains", params=params)

    async def concepts(
        self,
        domain_id: str,
        *,
        vocabulary_ids: builtins.list[str] | None = None,
        concept_class_ids: builtins.list[str] | None = None,
        standard_only: bool = False,
        page: int = 1,
        page_size: int = 50,
    ) -> dict[str, Any]:
        """Get concepts in a domain.

        Args:
            domain_id: The domain ID
            vocabulary_ids: Filter by vocabularies
            concept_class_ids: Filter by concept classes
            standard_only: Only standard concepts
            page: Page number
            page_size: Results per page

        Returns:
            Paginated concepts
        """
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if vocabulary_ids:
            params["vocabulary_ids"] = ",".join(vocabulary_ids)
        if concept_class_ids:
            params["concept_class_ids"] = ",".join(concept_class_ids)
        if standard_only:
            params["standard_only"] = "true"

        return await self._request.get(f"/domains/{domain_id}/concepts", params=params)
