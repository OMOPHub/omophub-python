"""FHIR Resolver resource implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .._request import AsyncRequest, Request
    from ..types.fhir import (
        CodeableConcept,
        CodeableConceptLike,
        Coding,
        CodingLike,
        FhirBatchResult,
        FhirCodeableConceptResult,
        FhirResolveResult,
    )

    CodingInput = Coding | CodingLike | dict[str, Any]
    CodeableConceptInput = CodeableConcept | CodeableConceptLike | dict[str, Any]


def _extract_coding(
    coding_input: object,
) -> tuple[str | None, str | None, str | None]:
    """Normalize any Coding-like input to ``(system, code, display)``.

    Accepts plain dicts, the ``omophub.types.fhir.Coding`` TypedDict,
    ``fhir.resources.Coding`` instances, ``fhirpy`` codings, or any user
    object exposing ``.system`` / ``.code`` / ``.display`` attributes.
    """
    if isinstance(coding_input, dict):
        return (
            coding_input.get("system"),
            coding_input.get("code"),
            coding_input.get("display"),
        )
    return (
        getattr(coding_input, "system", None),
        getattr(coding_input, "code", None),
        getattr(coding_input, "display", None),
    )


# Keys the FHIR Concept Resolver accepts on a single coding item. Any
# other keys in a dict input (e.g. ``userSelected``, ``extension``,
# ``version`` from ``fhir.resources.Coding.model_dump()``) are dropped
# so the server never sees FHIR metadata it does not understand.
_ALLOWED_CODING_KEYS: tuple[str, ...] = (
    "system",
    "code",
    "display",
    "vocabulary_id",
)


def _coding_to_dict(coding_input: object) -> dict[str, Any]:
    """Convert any Coding-like input to a wire-format dict.

    Preserves only the keys the resolver endpoint understands
    (:data:`_ALLOWED_CODING_KEYS`). Skips keys whose values are ``None``
    so the request payload stays tight.
    """
    if isinstance(coding_input, dict):
        src: dict[str, Any] = {
            key: coding_input.get(key) for key in _ALLOWED_CODING_KEYS
        }
    else:
        src = {key: getattr(coding_input, key, None) for key in _ALLOWED_CODING_KEYS}
    return {k: v for k, v in src.items() if v is not None}


def _extract_codeable_concept(
    cc_input: object,
) -> tuple[list[object], str | None]:
    """Normalize any CodeableConcept-like input to ``(codings, text)``."""
    if isinstance(cc_input, dict):
        codings = cc_input.get("coding") or []
        text = cc_input.get("text")
    else:
        codings = getattr(cc_input, "coding", None) or []
        text = getattr(cc_input, "text", None)
    if not isinstance(codings, list):
        codings = list(codings)
    return codings, text


def _resolve_coding_kwargs(
    coding: object | None,
    system: str | None,
    code: str | None,
    display: str | None,
) -> tuple[str | None, str | None, str | None]:
    """Merge explicit kwargs with an optional coding input.

    Explicit kwargs always win. Missing kwargs fall back to values
    extracted from ``coding``.
    """
    if coding is None:
        return system, code, display
    ext_system, ext_code, ext_display = _extract_coding(coding)
    return (
        system if system is not None else ext_system,
        code if code is not None else ext_code,
        display if display is not None else ext_display,
    )


def _normalize_codeable_concept_input(
    coding_input: object,
) -> tuple[list[object], str | None]:
    """Accept either a list of Coding-likes or a CodeableConcept-like.

    A bare list is treated as the ``coding`` array with no ``text``
    field. Any other object is passed through
    :func:`_extract_codeable_concept`.
    """
    if isinstance(coding_input, list):
        return coding_input, None
    return _extract_codeable_concept(coding_input)


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
        coding: CodingInput | None = None,
        vocabulary_id: str | None = None,
        resource_type: str | None = None,
        include_recommendations: bool = False,
        recommendations_limit: int = 5,
        include_quality: bool = False,
    ) -> FhirResolveResult:
        """Resolve a single FHIR Coding to an OMOP standard concept.

        Provide either explicit ``system`` + ``code`` kwargs, a ``coding``
        input (dict, :class:`~omophub.types.fhir.Coding` TypedDict, or any
        ``fhir.resources`` / ``fhirpy`` coding object with ``.system``
        / ``.code`` attributes), or ``vocabulary_id`` + ``code``, or
        ``display``.

        When both ``coding`` and explicit ``system``/``code`` are passed,
        the explicit kwargs take precedence.

        Args:
            system: FHIR code system URI (e.g. ``http://snomed.info/sct``)
            code: Code value from the FHIR Coding
            display: Human-readable text (semantic search fallback)
            coding: Any Coding-like input - dict, TypedDict, or object
            vocabulary_id: Direct OMOP vocabulary_id, bypasses URI resolution
            resource_type: FHIR resource type for domain alignment check
            include_recommendations: Include Phoebe recommendations
            recommendations_limit: Max recommendations to return (1-20)
            include_quality: Include mapping quality signal

        Returns:
            Resolution result with source concept, standard concept,
            target CDM table, and optional enrichments.
        """
        resolved_system, resolved_code, resolved_display = _resolve_coding_kwargs(
            coding, system, code, display
        )
        body = _build_resolve_body(
            system=resolved_system,
            code=resolved_code,
            display=resolved_display,
            vocabulary_id=vocabulary_id,
            resource_type=resource_type,
            include_recommendations=include_recommendations,
            recommendations_limit=recommendations_limit,
            include_quality=include_quality,
        )
        return self._request.post("/fhir/resolve", json_data=body)

    def resolve_batch(
        self,
        codings: list[CodingInput],
        *,
        resource_type: str | None = None,
        include_recommendations: bool = False,
        recommendations_limit: int = 5,
        include_quality: bool = False,
    ) -> FhirBatchResult:
        """Batch-resolve up to 100 FHIR Codings.

        Failed items are reported inline without failing the batch.

        Args:
            codings: List of Coding-like inputs. Each item may be a plain
                     dict with ``system`` / ``code`` / ``display`` /
                     ``vocabulary_id`` keys, an
                     :class:`~omophub.types.fhir.Coding` TypedDict, or any
                     object exposing ``.system`` / ``.code`` attributes
                     (e.g. ``fhir.resources.Coding``, ``fhirpy`` codings).
            resource_type: FHIR resource type applied to all codings
            include_recommendations: Include Phoebe recommendations
            recommendations_limit: Max recommendations per item (1-20)
            include_quality: Include mapping quality signal

        Returns:
            Batch result with per-item results and a summary.
        """
        body: dict[str, Any] = {"codings": [_coding_to_dict(c) for c in codings]}
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
        coding: list[CodingInput] | CodeableConceptInput,
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
            coding: Either a list of Coding-like inputs (same shapes
                    accepted by :meth:`resolve_batch`), or a full
                    CodeableConcept-like object exposing ``.coding``
                    and ``.text`` (``omophub.types.fhir.CodeableConcept``,
                    ``fhir.resources.CodeableConcept``, or a dict).
            text: CodeableConcept.text for semantic search fallback.
                  When ``coding`` is a CodeableConcept-like object, this
                  kwarg overrides its ``text`` field if provided.
            resource_type: FHIR resource type for domain alignment
            include_recommendations: Include Phoebe recommendations
            recommendations_limit: Max recommendations (1-20)
            include_quality: Include mapping quality signal

        Returns:
            Result with ``best_match``, ``alternatives``, and
            ``unresolved`` lists.
        """
        codings_list, extracted_text = _normalize_codeable_concept_input(coding)
        final_text = text if text is not None else extracted_text
        body: dict[str, Any] = {"coding": [_coding_to_dict(c) for c in codings_list]}
        if final_text is not None:
            body["text"] = final_text
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
        coding: CodingInput | None = None,
        vocabulary_id: str | None = None,
        resource_type: str | None = None,
        include_recommendations: bool = False,
        recommendations_limit: int = 5,
        include_quality: bool = False,
    ) -> FhirResolveResult:
        """Resolve a single FHIR Coding to an OMOP standard concept.

        See :meth:`Fhir.resolve` for full documentation.
        """
        resolved_system, resolved_code, resolved_display = _resolve_coding_kwargs(
            coding, system, code, display
        )
        body = _build_resolve_body(
            system=resolved_system,
            code=resolved_code,
            display=resolved_display,
            vocabulary_id=vocabulary_id,
            resource_type=resource_type,
            include_recommendations=include_recommendations,
            recommendations_limit=recommendations_limit,
            include_quality=include_quality,
        )
        return await self._request.post("/fhir/resolve", json_data=body)

    async def resolve_batch(
        self,
        codings: list[CodingInput],
        *,
        resource_type: str | None = None,
        include_recommendations: bool = False,
        recommendations_limit: int = 5,
        include_quality: bool = False,
    ) -> FhirBatchResult:
        """Batch-resolve up to 100 FHIR Codings.

        See :meth:`Fhir.resolve_batch` for full documentation.
        """
        body: dict[str, Any] = {"codings": [_coding_to_dict(c) for c in codings]}
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
        coding: list[CodingInput] | CodeableConceptInput,
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
        codings_list, extracted_text = _normalize_codeable_concept_input(coding)
        final_text = text if text is not None else extracted_text
        body: dict[str, Any] = {"coding": [_coding_to_dict(c) for c in codings_list]}
        if final_text is not None:
            body["text"] = final_text
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
