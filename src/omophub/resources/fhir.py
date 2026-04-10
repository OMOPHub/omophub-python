"""FHIR Resolver resource implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .._request import AsyncRequest, Request
    from ..types.fhir import (
        FhirBatchResult,
        FhirCodeableConceptResult,
        FhirResolveResult,
    )


def _build_resolve_body(
    *,
    system: str | None = None,
    code: str | None = None,
    display: str | None = None,
    vocabulary_id: str | None = None,
    resource_type: str | None = None,
    include_recommendations: bool = False,
    recommendations_limit: int = 5,
    include_quality: bool = False,
) -> dict[str, Any]:
    body: dict[str, Any] = {}
    if system is not None:
        body["system"] = system
    if code is not None:
        body["code"] = code
    if display is not None:
        body["display"] = display
    if vocabulary_id is not None:
        body["vocabulary_id"] = vocabulary_id
    if resource_type is not None:
        body["resource_type"] = resource_type
    if include_recommendations:
        body["include_recommendations"] = True
        body["recommendations_limit"] = recommendations_limit
    if include_quality:
        body["include_quality"] = True
    return body


class Fhir:
    """Synchronous FHIR resolver resource.

    Provides access to the FHIR-to-OMOP Concept Resolver endpoints that
    translate FHIR coded values into OMOP standard concepts, CDM target
    tables, and optional Phoebe recommendations.

    Example:
        >>> result = client.fhir.resolve(
        ...     system="http://snomed.info/sct",
        ...     code="44054006",
        ...     resource_type="Condition",
        ... )
        >>> print(result["resolution"]["target_table"])
        "condition_occurrence"
    """

    def __init__(self, request: Request[Any]) -> None:
        self._request = request

    def resolve(
        self,
        *,
        system: str | None = None,
        code: str | None = None,
        display: str | None = None,
        vocabulary_id: str | None = None,
        resource_type: str | None = None,
        include_recommendations: bool = False,
        recommendations_limit: int = 5,
        include_quality: bool = False,
    ) -> FhirResolveResult:
        """Resolve a single FHIR Coding to an OMOP standard concept.

        Provide at least one of (``system`` + ``code``),
        (``vocabulary_id`` + ``code``), or ``display``.

        Args:
            system: FHIR code system URI (e.g. ``http://snomed.info/sct``)
            code: Code value from the FHIR Coding
            display: Human-readable text (semantic search fallback)
            vocabulary_id: Direct OMOP vocabulary_id, bypasses URI resolution
            resource_type: FHIR resource type for domain alignment check
            include_recommendations: Include Phoebe recommendations
            recommendations_limit: Max recommendations to return (1-20)
            include_quality: Include mapping quality signal

        Returns:
            Resolution result with source concept, standard concept,
            target CDM table, and optional enrichments.
        """
        body = _build_resolve_body(
            system=system,
            code=code,
            display=display,
            vocabulary_id=vocabulary_id,
            resource_type=resource_type,
            include_recommendations=include_recommendations,
            recommendations_limit=recommendations_limit,
            include_quality=include_quality,
        )
        return self._request.post("/fhir/resolve", json_data=body)

    def resolve_batch(
        self,
        codings: list[dict[str, str | None]],
        *,
        resource_type: str | None = None,
        include_recommendations: bool = False,
        recommendations_limit: int = 5,
        include_quality: bool = False,
    ) -> FhirBatchResult:
        """Batch-resolve up to 100 FHIR Codings.

        Failed items are reported inline without failing the batch.

        Args:
            codings: List of coding dicts, each with optional keys
                     ``system``, ``code``, ``display``, ``vocabulary_id``.
            resource_type: FHIR resource type applied to all codings
            include_recommendations: Include Phoebe recommendations
            recommendations_limit: Max recommendations per item (1-20)
            include_quality: Include mapping quality signal

        Returns:
            Batch result with per-item results and a summary.
        """
        body: dict[str, Any] = {"codings": codings}
        if resource_type is not None:
            body["resource_type"] = resource_type
        if include_recommendations:
            body["include_recommendations"] = True
            body["recommendations_limit"] = recommendations_limit
        if include_quality:
            body["include_quality"] = True
        return self._request.post("/fhir/resolve/batch", json_data=body)

    def resolve_codeable_concept(
        self,
        coding: list[dict[str, str]],
        *,
        text: str | None = None,
        resource_type: str | None = None,
        include_recommendations: bool = False,
        recommendations_limit: int = 5,
        include_quality: bool = False,
    ) -> FhirCodeableConceptResult:
        """Resolve a FHIR CodeableConcept with vocabulary preference.

        Picks the best match across multiple codings using the OHDSI
        vocabulary preference order (SNOMED > RxNorm > LOINC > CVX >
        ICD-10). Falls back to ``text`` via semantic search if no
        coding resolves.

        Args:
            coding: List of structured codings, each with ``system``,
                    ``code``, and optional ``display``.
            text: CodeableConcept.text for semantic search fallback
            resource_type: FHIR resource type for domain alignment
            include_recommendations: Include Phoebe recommendations
            recommendations_limit: Max recommendations (1-20)
            include_quality: Include mapping quality signal

        Returns:
            Result with ``best_match``, ``alternatives``, and
            ``unresolved`` lists.
        """
        body: dict[str, Any] = {"coding": coding}
        if text is not None:
            body["text"] = text
        if resource_type is not None:
            body["resource_type"] = resource_type
        if include_recommendations:
            body["include_recommendations"] = True
            body["recommendations_limit"] = recommendations_limit
        if include_quality:
            body["include_quality"] = True
        return self._request.post("/fhir/resolve/codeable-concept", json_data=body)


class AsyncFhir:
    """Asynchronous FHIR resolver resource.

    Async counterpart of :class:`Fhir`. All methods are coroutines.
    """

    def __init__(self, request: AsyncRequest[Any]) -> None:
        self._request = request

    async def resolve(
        self,
        *,
        system: str | None = None,
        code: str | None = None,
        display: str | None = None,
        vocabulary_id: str | None = None,
        resource_type: str | None = None,
        include_recommendations: bool = False,
        recommendations_limit: int = 5,
        include_quality: bool = False,
    ) -> FhirResolveResult:
        """Resolve a single FHIR Coding to an OMOP standard concept.

        See :meth:`Fhir.resolve` for full documentation.
        """
        body = _build_resolve_body(
            system=system,
            code=code,
            display=display,
            vocabulary_id=vocabulary_id,
            resource_type=resource_type,
            include_recommendations=include_recommendations,
            recommendations_limit=recommendations_limit,
            include_quality=include_quality,
        )
        return await self._request.post("/fhir/resolve", json_data=body)

    async def resolve_batch(
        self,
        codings: list[dict[str, str | None]],
        *,
        resource_type: str | None = None,
        include_recommendations: bool = False,
        recommendations_limit: int = 5,
        include_quality: bool = False,
    ) -> FhirBatchResult:
        """Batch-resolve up to 100 FHIR Codings.

        See :meth:`Fhir.resolve_batch` for full documentation.
        """
        body: dict[str, Any] = {"codings": codings}
        if resource_type is not None:
            body["resource_type"] = resource_type
        if include_recommendations:
            body["include_recommendations"] = True
            body["recommendations_limit"] = recommendations_limit
        if include_quality:
            body["include_quality"] = True
        return await self._request.post("/fhir/resolve/batch", json_data=body)

    async def resolve_codeable_concept(
        self,
        coding: list[dict[str, str]],
        *,
        text: str | None = None,
        resource_type: str | None = None,
        include_recommendations: bool = False,
        recommendations_limit: int = 5,
        include_quality: bool = False,
    ) -> FhirCodeableConceptResult:
        """Resolve a FHIR CodeableConcept with vocabulary preference.

        See :meth:`Fhir.resolve_codeable_concept` for full documentation.
        """
        body: dict[str, Any] = {"coding": coding}
        if text is not None:
            body["text"] = text
        if resource_type is not None:
            body["resource_type"] = resource_type
        if include_recommendations:
            body["include_recommendations"] = True
            body["recommendations_limit"] = recommendations_limit
        if include_quality:
            body["include_quality"] = True
        return await self._request.post(
            "/fhir/resolve/codeable-concept", json_data=body
        )
