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
        include_stats: bool = False,
    ) -> dict[str, Any]:
        """List all domains.

        Args:
            include_stats: Include concept counts and vocabulary coverage

        Returns:
            Domain list
        """
        params: dict[str, Any] = {}
        if include_stats:
            params["include_stats"] = "true"

        return self._request.get("/domains", params=params)

    def concepts(
        self,
        domain_id: str,
        *,
        vocabulary_ids: builtins.list[str] | None = None,
        standard_only: bool = False,
        include_invalid: bool = False,
        page: int = 1,
        page_size: int = 50,
    ) -> dict[str, Any]:
        """Get concepts in a domain.

        Args:
            domain_id: The domain ID
            vocabulary_ids: Filter by vocabularies
            standard_only: Only standard concepts
            include_invalid: Include invalid/deprecated concepts
            page: Page number
            page_size: Results per page

        Returns:
            Paginated concepts
        """
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if vocabulary_ids:
            params["vocabulary_ids"] = ",".join(vocabulary_ids)
        if standard_only:
            params["standard_only"] = "true"
        if include_invalid:
            params["include_invalid"] = "true"

        return self._request.get(f"/domains/{domain_id}/concepts", params=params)


class AsyncDomains:
    """Asynchronous domains resource."""

    def __init__(self, request: AsyncRequest[Any]) -> None:
        self._request = request

    async def list(
        self,
        *,
        include_stats: bool = False,
    ) -> dict[str, Any]:
        """List all domains.

        Args:
            include_stats: Include concept counts and vocabulary coverage

        Returns:
            Domain list
        """
        params: dict[str, Any] = {}
        if include_stats:
            params["include_stats"] = "true"

        return await self._request.get("/domains", params=params)

    async def concepts(
        self,
        domain_id: str,
        *,
        vocabulary_ids: builtins.list[str] | None = None,
        standard_only: bool = False,
        include_invalid: bool = False,
        page: int = 1,
        page_size: int = 50,
    ) -> dict[str, Any]:
        """Get concepts in a domain.

        Args:
            domain_id: The domain ID
            vocabulary_ids: Filter by vocabularies
            standard_only: Only standard concepts
            include_invalid: Include invalid/deprecated concepts
            page: Page number
            page_size: Results per page

        Returns:
            Paginated concepts
        """
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if vocabulary_ids:
            params["vocabulary_ids"] = ",".join(vocabulary_ids)
        if standard_only:
            params["standard_only"] = "true"
        if include_invalid:
            params["include_invalid"] = "true"

        return await self._request.get(f"/domains/{domain_id}/concepts", params=params)
