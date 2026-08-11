"""Mappings resource implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .._pagination import paginate_async, paginate_sync

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from .._request import AsyncRequest, Request
    from .._types import PaginationMeta


class Mappings:
    """Synchronous mappings resource."""

    def __init__(self, request: Request[Any]) -> None:
        self._request = request

    def get(
        self,
        concept_id: int,
        *,
        target_vocabulary: str | None = None,
        relationship_ids: str | list[str] | None = None,
        include_invalid: bool | None = None,
        page: int = 1,
        page_size: int = 100,
        vocab_release: str | None = None,
    ) -> dict[str, Any]:
        """Get mappings for a concept.

        A concept can have more mappings than one page carries, and this
        method returns the ``data`` field only — the pagination metadata that
        would tell you so is not part of what you get back. Use
        :meth:`get_iter` when you need every mapping, and treat a full page here
        as "there is probably more" rather than as the complete set.

        Args:
            concept_id: The concept ID
            target_vocabulary: Filter to a specific target vocabulary (e.g., "ICD10CM")
            relationship_ids: Relationship types to return, as a list or a
                comma-separated string. Defaults server-side to ``["Maps to"]``.
                Pass ``["Maps to", "Maps to value"]`` to also get the
                Value-as-Concept decomposition of composite concepts -- e.g.
                "Allergy to penicillin G" maps to "Allergy to drug" via
                ``Maps to`` and to "penicillin G" via ``Maps to value``, and the
                default returns only the first of those.
            include_invalid: Whether to return mappings whose relationship or
                target concept is deprecated. Omit to take the server default,
                which for this endpoint is to **include** them; pass ``False``
                to exclude them. The source concept is never filtered, so a
                deprecated concept still returns what it maps to.
            page: Page number, 1-based (default 1)
            page_size: Mappings per page (default 100). The server clamps this to
                200 on this endpoint and does not report having done so, so a
                larger value silently yields a smaller page.
            vocab_release: Specific vocabulary release version (e.g., "2025.1")

        Returns:
            The response ``data`` field only. ``meta.pagination`` is **not**
            part of it, so nothing in this return value tells you whether the
            mappings were truncated -- use :meth:`get_iter` when that matters.
        """
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if target_vocabulary:
            params["target_vocabulary"] = target_vocabulary
        if relationship_ids:
            params["relationship_ids"] = (
                ",".join(relationship_ids)
                if isinstance(relationship_ids, list)
                else relationship_ids
            )
        if include_invalid is not None:
            params["include_invalid"] = "true" if include_invalid else "false"
        if vocab_release:
            params["vocab_release"] = vocab_release

        return self._request.get(
            f"/concepts/{concept_id}/mappings", params=params or None
        )

    def get_iter(
        self,
        concept_id: int,
        *,
        target_vocabulary: str | None = None,
        relationship_ids: str | list[str] | None = None,
        include_invalid: bool | None = None,
        page_size: int = 100,
        vocab_release: str | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Iterate over every mapping for a concept, across all pages.

        Prefer this to :meth:`get` when you are building a code list. A single
        page is capped server-side, so a concept with more mappings than the
        page size yields a subset that looks exactly like a complete answer.

        Args:
            concept_id: The concept ID
            target_vocabulary: Filter to a specific target vocabulary (e.g., "ICD10CM")
            relationship_ids: Relationship types to return, as a list or a
                comma-separated string. Defaults server-side to ``["Maps to"]``.
                Pass ``["Maps to", "Maps to value"]`` to also get the
                Value-as-Concept decomposition of composite concepts -- e.g.
                "Allergy to penicillin G" maps to "Allergy to drug" via
                ``Maps to`` and to "penicillin G" via ``Maps to value``, and the
                default returns only the first of those.
            include_invalid: Whether to return mappings whose relationship or
                target concept is deprecated. Omit to take the server default,
                which for this endpoint is to **include** them; pass ``False``
                to exclude them. The source concept is never filtered, so a
                deprecated concept still returns what it maps to.
            page_size: Mappings fetched per request (default 100, server max 200)
            vocab_release: Specific vocabulary release version (e.g., "2025.1")

        Yields:
            Individual mappings from all pages
        """

        def fetch_page(
            page: int, size: int
        ) -> tuple[list[dict[str, Any]], PaginationMeta | None]:
            params: dict[str, Any] = {"page": page, "page_size": size}
            if target_vocabulary:
                params["target_vocabulary"] = target_vocabulary
            if relationship_ids:
                params["relationship_ids"] = (
                    ",".join(relationship_ids)
                    if isinstance(relationship_ids, list)
                    else relationship_ids
                )
            if include_invalid is not None:
                params["include_invalid"] = "true" if include_invalid else "false"
            if vocab_release:
                params["vocab_release"] = vocab_release

            # get_raw() rather than get(): the pagination meta is the entire
            # point here and get() discards it.
            result = self._request.get_raw(
                f"/concepts/{concept_id}/mappings", params=params
            )
            data = result.get("data") or {}
            mappings = data.get("mappings", []) if isinstance(data, dict) else data
            meta = result.get("meta", {}).get("pagination")
            return mappings, meta

        yield from paginate_sync(fetch_page, page_size)

    def map(
        self,
        target_vocabulary: str,
        *,
        source_concepts: list[int] | None = None,
        source_codes: list[dict[str, str]] | None = None,
        mapping_type: str | None = None,
        include_invalid: bool = False,
        vocab_release: str | None = None,
    ) -> dict[str, Any]:
        """Map concepts to a target vocabulary.

        Args:
            target_vocabulary: Target vocabulary ID (e.g., "ICD10CM", "SNOMED", "RxNorm")
            source_concepts: List of OMOP concept IDs to map. Use this OR source_codes,
                not both.
            source_codes: List of vocabulary/code pairs to map, e.g.,
                [{"vocabulary_id": "SNOMED", "concept_code": "387517004"}].
                Use this OR source_concepts, not both.
            mapping_type: Mapping type filter (direct, equivalent, broader, narrower)
            include_invalid: Include invalid mappings
            vocab_release: Specific vocabulary release version (e.g., "2025.1")

        Returns:
            Mapping results with summary

        Raises:
            ValueError: If neither or both source_concepts and source_codes are provided
        """
        # Validate: exactly one of source_concepts or source_codes required
        has_concepts = source_concepts is not None and len(source_concepts) > 0
        has_codes = source_codes is not None and len(source_codes) > 0

        if not has_concepts and not has_codes:
            raise ValueError("Either source_concepts or source_codes is required")
        if has_concepts and has_codes:
            raise ValueError("Cannot use both source_concepts and source_codes")

        body: dict[str, Any] = {
            "target_vocabulary": target_vocabulary,
        }

        if source_concepts:
            body["source_concepts"] = source_concepts
        if source_codes:
            body["source_codes"] = source_codes
        if mapping_type:
            body["mapping_type"] = mapping_type
        if include_invalid:
            body["include_invalid"] = True

        params: dict[str, Any] = {}
        if vocab_release:
            params["vocab_release"] = vocab_release

        return self._request.post(
            "/concepts/map", json_data=body, params=params or None
        )


class AsyncMappings:
    """Asynchronous mappings resource."""

    def __init__(self, request: AsyncRequest[Any]) -> None:
        self._request = request

    async def get(
        self,
        concept_id: int,
        *,
        target_vocabulary: str | None = None,
        relationship_ids: str | list[str] | None = None,
        include_invalid: bool | None = None,
        page: int = 1,
        page_size: int = 100,
        vocab_release: str | None = None,
    ) -> dict[str, Any]:
        """Get mappings for a concept.

        A concept can have more mappings than one page carries, and this
        method returns the ``data`` field only — the pagination metadata that
        would tell you so is not part of what you get back. Use
        :meth:`get_iter` when you need every mapping, and treat a full page here
        as "there is probably more" rather than as the complete set.

        Args:
            concept_id: The concept ID
            target_vocabulary: Filter to a specific target vocabulary (e.g., "ICD10CM")
            relationship_ids: Relationship types to return, as a list or a
                comma-separated string. Defaults server-side to ``["Maps to"]``.
                Pass ``["Maps to", "Maps to value"]`` to also get the
                Value-as-Concept decomposition of composite concepts -- e.g.
                "Allergy to penicillin G" maps to "Allergy to drug" via
                ``Maps to`` and to "penicillin G" via ``Maps to value``, and the
                default returns only the first of those.
            include_invalid: Whether to return mappings whose relationship or
                target concept is deprecated. Omit to take the server default,
                which for this endpoint is to **include** them; pass ``False``
                to exclude them. The source concept is never filtered, so a
                deprecated concept still returns what it maps to.
            page: Page number, 1-based (default 1)
            page_size: Mappings per page (default 100). The server clamps this to
                200 on this endpoint and does not report having done so, so a
                larger value silently yields a smaller page.
            vocab_release: Specific vocabulary release version (e.g., "2025.1")

        Returns:
            The response ``data`` field only. ``meta.pagination`` is **not**
            part of it, so nothing in this return value tells you whether the
            mappings were truncated -- use :meth:`get_iter` when that matters.
        """
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if target_vocabulary:
            params["target_vocabulary"] = target_vocabulary
        if relationship_ids:
            params["relationship_ids"] = (
                ",".join(relationship_ids)
                if isinstance(relationship_ids, list)
                else relationship_ids
            )
        if include_invalid is not None:
            params["include_invalid"] = "true" if include_invalid else "false"
        if vocab_release:
            params["vocab_release"] = vocab_release

        return await self._request.get(
            f"/concepts/{concept_id}/mappings", params=params or None
        )

    async def get_iter(
        self,
        concept_id: int,
        *,
        target_vocabulary: str | None = None,
        relationship_ids: str | list[str] | None = None,
        include_invalid: bool | None = None,
        page_size: int = 100,
        vocab_release: str | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """Iterate over every mapping for a concept, across all pages.

        Prefer this to :meth:`get` when you are building a code list. A single
        page is capped server-side, so a concept with more mappings than the
        page size yields a subset that looks exactly like a complete answer.

        Args:
            concept_id: The concept ID
            target_vocabulary: Filter to a specific target vocabulary (e.g., "ICD10CM")
            relationship_ids: Relationship types to return, as a list or a
                comma-separated string. Defaults server-side to ``["Maps to"]``.
                Pass ``["Maps to", "Maps to value"]`` to also get the
                Value-as-Concept decomposition of composite concepts -- e.g.
                "Allergy to penicillin G" maps to "Allergy to drug" via
                ``Maps to`` and to "penicillin G" via ``Maps to value``, and the
                default returns only the first of those.
            include_invalid: Whether to return mappings whose relationship or
                target concept is deprecated. Omit to take the server default,
                which for this endpoint is to **include** them; pass ``False``
                to exclude them. The source concept is never filtered, so a
                deprecated concept still returns what it maps to.
            page_size: Mappings fetched per request (default 100, server max 200)
            vocab_release: Specific vocabulary release version (e.g., "2025.1")

        Yields:
            Individual mappings from all pages
        """

        async def fetch_page(
            page: int, size: int
        ) -> tuple[list[dict[str, Any]], PaginationMeta | None]:
            params: dict[str, Any] = {"page": page, "page_size": size}
            if target_vocabulary:
                params["target_vocabulary"] = target_vocabulary
            if relationship_ids:
                params["relationship_ids"] = (
                    ",".join(relationship_ids)
                    if isinstance(relationship_ids, list)
                    else relationship_ids
                )
            if include_invalid is not None:
                params["include_invalid"] = "true" if include_invalid else "false"
            if vocab_release:
                params["vocab_release"] = vocab_release

            # get_raw() rather than get(): the pagination meta is the entire
            # point here and get() discards it.
            result = await self._request.get_raw(
                f"/concepts/{concept_id}/mappings", params=params
            )
            data = result.get("data") or {}
            mappings = data.get("mappings", []) if isinstance(data, dict) else data
            meta = result.get("meta", {}).get("pagination")
            return mappings, meta

        async for item in paginate_async(fetch_page, page_size):
            yield item

    async def map(
        self,
        target_vocabulary: str,
        *,
        source_concepts: list[int] | None = None,
        source_codes: list[dict[str, str]] | None = None,
        mapping_type: str | None = None,
        include_invalid: bool = False,
        vocab_release: str | None = None,
    ) -> dict[str, Any]:
        """Map concepts to a target vocabulary.

        Args:
            target_vocabulary: Target vocabulary ID (e.g., "ICD10CM", "SNOMED", "RxNorm")
            source_concepts: List of OMOP concept IDs to map. Use this OR source_codes,
                not both.
            source_codes: List of vocabulary/code pairs to map, e.g.,
                [{"vocabulary_id": "SNOMED", "concept_code": "387517004"}].
                Use this OR source_concepts, not both.
            mapping_type: Mapping type filter (direct, equivalent, broader, narrower)
            include_invalid: Include invalid mappings
            vocab_release: Specific vocabulary release version (e.g., "2025.1")

        Returns:
            Mapping results with summary

        Raises:
            ValueError: If neither or both source_concepts and source_codes are provided
        """
        # Validate: exactly one of source_concepts or source_codes required
        has_concepts = source_concepts is not None and len(source_concepts) > 0
        has_codes = source_codes is not None and len(source_codes) > 0

        if not has_concepts and not has_codes:
            raise ValueError("Either source_concepts or source_codes is required")
        if has_concepts and has_codes:
            raise ValueError("Cannot use both source_concepts and source_codes")

        body: dict[str, Any] = {
            "target_vocabulary": target_vocabulary,
        }

        if source_concepts:
            body["source_concepts"] = source_concepts
        if source_codes:
            body["source_codes"] = source_codes
        if mapping_type:
            body["mapping_type"] = mapping_type
        if include_invalid:
            body["include_invalid"] = True

        params: dict[str, Any] = {}
        if vocab_release:
            params["vocab_release"] = vocab_release

        return await self._request.post(
            "/concepts/map", json_data=body, params=params or None
        )
