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
        source_concepts: list[int],
        target_vocabulary: str,
        *,
        mapping_type: str | None = None,
        include_invalid: bool = False,
        vocab_release: str | None = None,
    ) -> dict[str, Any]:
        """Map concepts to a target vocabulary.

        Args:
            source_concepts: List of OMOP concept IDs to map
            target_vocabulary: Target vocabulary ID (e.g., "ICD10CM", "SNOMED")
            mapping_type: Mapping type (direct, equivalent, broader, narrower)
            include_invalid: Include invalid mappings
            vocab_release: Specific vocabulary release version (e.g., "2025.1")

        Returns:
            Mapping results with summary
        """
        body: dict[str, Any] = {
            "source_concepts": source_concepts,
            "target_vocabulary": target_vocabulary,
        }
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
        source_concepts: list[int],
        target_vocabulary: str,
        *,
        mapping_type: str | None = None,
        include_invalid: bool = False,
        vocab_release: str | None = None,
    ) -> dict[str, Any]:
        """Map concepts to a target vocabulary.

        Args:
            source_concepts: List of OMOP concept IDs to map
            target_vocabulary: Target vocabulary ID (e.g., "ICD10CM", "SNOMED")
            mapping_type: Mapping type (direct, equivalent, broader, narrower)
            include_invalid: Include invalid mappings
            vocab_release: Specific vocabulary release version (e.g., "2025.1")

        Returns:
            Mapping results with summary
        """
        body: dict[str, Any] = {
            "source_concepts": source_concepts,
            "target_vocabulary": target_vocabulary,
        }
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
