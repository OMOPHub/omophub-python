"""Mappings resource implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .._request import AsyncRequest, Request


class Mappings:
    """Synchronous mappings resource."""

    def __init__(self, request: Request[Any]) -> None:
        self._request = request

    def get(
        self,
        concept_id: int,
        *,
        target_vocabulary: str | None = None,
        include_invalid: bool = False,
        vocab_release: str | None = None,
    ) -> dict[str, Any]:
        """Get mappings for a concept.

        Args:
            concept_id: The concept ID
            target_vocabulary: Filter to a specific target vocabulary (e.g., "ICD10CM")
            include_invalid: Include invalid/deprecated mappings
            vocab_release: Specific vocabulary release version (e.g., "2025.1")

        Returns:
            Mappings for the concept
        """
        params: dict[str, Any] = {}
        if target_vocabulary:
            params["target_vocabulary"] = target_vocabulary
        if include_invalid:
            params["include_invalid"] = "true"
        if vocab_release:
            params["vocab_release"] = vocab_release

        return self._request.get(
            f"/concepts/{concept_id}/mappings", params=params or None
        )

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
        include_invalid: bool = False,
        vocab_release: str | None = None,
    ) -> dict[str, Any]:
        """Get mappings for a concept.

        Args:
            concept_id: The concept ID
            target_vocabulary: Filter to a specific target vocabulary (e.g., "ICD10CM")
            include_invalid: Include invalid/deprecated mappings
            vocab_release: Specific vocabulary release version (e.g., "2025.1")

        Returns:
            Mappings for the concept
        """
        params: dict[str, Any] = {}
        if target_vocabulary:
            params["target_vocabulary"] = target_vocabulary
        if include_invalid:
            params["include_invalid"] = "true"
        if vocab_release:
            params["vocab_release"] = vocab_release

        return await self._request.get(
            f"/concepts/{concept_id}/mappings", params=params or None
        )

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
