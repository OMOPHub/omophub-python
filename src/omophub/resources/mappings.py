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
        target_vocabularies: list[str] | None = None,
        mapping_types: list[str] | None = None,
        direction: str = "both",
        include_indirect: bool = False,
        standard_only: bool = False,
        include_mapping_quality: bool = False,
        include_synonyms: bool = False,
        include_context: bool = False,
        active_only: bool = True,
        sort_by: str | None = None,
        sort_order: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> dict[str, Any]:
        """Get mappings for a concept.

        Args:
            concept_id: The concept ID
            target_vocabularies: Filter by target vocabularies
            mapping_types: Filter by mapping types
            direction: Mapping direction ("outgoing", "incoming", "both")
            include_indirect: Include indirect mappings
            standard_only: Only standard concept mappings
            include_mapping_quality: Include quality metrics
            include_synonyms: Include synonyms
            include_context: Include mapping context
            active_only: Only active mappings
            sort_by: Sort field
            sort_order: Sort order
            page: Page number
            page_size: Results per page

        Returns:
            Mappings with summary
        """
        params: dict[str, Any] = {
            "direction": direction,
            "page": page,
            "page_size": page_size,
        }
        if target_vocabularies:
            params["target_vocabularies"] = ",".join(target_vocabularies)
        if mapping_types:
            params["mapping_types"] = ",".join(mapping_types)
        if include_indirect:
            params["include_indirect"] = "true"
        if standard_only:
            params["standard_only"] = "true"
        if include_mapping_quality:
            params["include_mapping_quality"] = "true"
        if include_synonyms:
            params["include_synonyms"] = "true"
        if include_context:
            params["include_context"] = "true"
        if not active_only:
            params["active_only"] = "false"
        if sort_by:
            params["sort_by"] = sort_by
        if sort_order:
            params["sort_order"] = sort_order

        return self._request.get(f"/concepts/{concept_id}/mappings", params=params)

    def map(
        self,
        source_concepts: list[int],
        target_vocabulary: str,
        *,
        mapping_type: str | None = None,
        include_invalid: bool = False,
    ) -> dict[str, Any]:
        """Map concepts to a target vocabulary.

        Args:
            source_concepts: List of OMOP concept IDs to map
            target_vocabulary: Target vocabulary ID (e.g., "ICD10CM", "SNOMED")
            mapping_type: Mapping type (direct, equivalent, broader, narrower)
            include_invalid: Include invalid mappings

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

        return self._request.post("/concepts/map", json_data=body)


class AsyncMappings:
    """Asynchronous mappings resource."""

    def __init__(self, request: AsyncRequest[Any]) -> None:
        self._request = request

    async def get(
        self,
        concept_id: int,
        *,
        target_vocabularies: list[str] | None = None,
        mapping_types: list[str] | None = None,
        direction: str = "both",
        include_indirect: bool = False,
        standard_only: bool = False,
        include_mapping_quality: bool = False,
        include_synonyms: bool = False,
        include_context: bool = False,
        active_only: bool = True,
        sort_by: str | None = None,
        sort_order: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> dict[str, Any]:
        """Get mappings for a concept.

        Args:
            concept_id: The concept ID
            target_vocabularies: Filter by target vocabularies
            mapping_types: Filter by mapping types
            direction: Mapping direction ("outgoing", "incoming", "both")
            include_indirect: Include indirect mappings
            standard_only: Only standard concept mappings
            include_mapping_quality: Include quality metrics
            include_synonyms: Include synonyms
            include_context: Include mapping context
            active_only: Only active mappings
            sort_by: Sort field
            sort_order: Sort order
            page: Page number
            page_size: Results per page

        Returns:
            Mappings with summary
        """
        params: dict[str, Any] = {
            "direction": direction,
            "page": page,
            "page_size": page_size,
        }
        if target_vocabularies:
            params["target_vocabularies"] = ",".join(target_vocabularies)
        if mapping_types:
            params["mapping_types"] = ",".join(mapping_types)
        if include_indirect:
            params["include_indirect"] = "true"
        if standard_only:
            params["standard_only"] = "true"
        if include_mapping_quality:
            params["include_mapping_quality"] = "true"
        if include_synonyms:
            params["include_synonyms"] = "true"
        if include_context:
            params["include_context"] = "true"
        if not active_only:
            params["active_only"] = "false"
        if sort_by:
            params["sort_by"] = sort_by
        if sort_order:
            params["sort_order"] = sort_order

        return await self._request.get(
            f"/concepts/{concept_id}/mappings", params=params
        )

    async def map(
        self,
        source_concepts: list[int],
        target_vocabulary: str,
        *,
        mapping_type: str | None = None,
        include_invalid: bool = False,
    ) -> dict[str, Any]:
        """Map concepts to a target vocabulary.

        Args:
            source_concepts: List of OMOP concept IDs to map
            target_vocabulary: Target vocabulary ID (e.g., "ICD10CM", "SNOMED")
            mapping_type: Mapping type (direct, equivalent, broader, narrower)
            include_invalid: Include invalid mappings

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

        return await self._request.post("/concepts/map", json_data=body)
