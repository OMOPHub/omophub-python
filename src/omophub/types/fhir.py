"""FHIR Resolver type definitions."""

from __future__ import annotations

from typing import Any, Protocol, TypedDict, runtime_checkable

from typing_extensions import NotRequired


class ResolvedConcept(TypedDict):
    """Concept shape returned by the FHIR resolver."""

    concept_id: int
    concept_name: str
    concept_code: str
    vocabulary_id: str
    domain_id: str
    concept_class_id: str
    standard_concept: str | None


class RecommendedConceptOutput(TypedDict):
    """Phoebe recommendation returned when include_recommendations is true."""

    concept_id: int
    concept_name: str
    vocabulary_id: str
    domain_id: str
    concept_class_id: str
    standard_concept: str | None
    relationship_id: str


class FhirResolution(TypedDict):
    """The ``resolution`` block inside a single-resolve response."""

    vocabulary_id: str | None
    source_concept: ResolvedConcept
    standard_concept: ResolvedConcept
    mapping_type: str
    target_table: str | None
    domain_resource_alignment: str
    relationship_id: NotRequired[str]
    similarity_score: NotRequired[float]
    alignment_note: NotRequired[str]
    mapping_quality: NotRequired[str]
    quality_note: NotRequired[str]
    alternative_standard_concepts: NotRequired[list[ResolvedConcept]]
    recommendations: NotRequired[list[RecommendedConceptOutput]]


class FhirResolveResult(TypedDict):
    """Response from ``POST /v1/fhir/resolve``."""

    input: dict[str, Any]
    resolution: FhirResolution


class FhirBatchSummary(TypedDict):
    """Summary block inside a batch-resolve response."""

    total: int
    resolved: int
    failed: int


class FhirBatchResult(TypedDict):
    """Response from ``POST /v1/fhir/resolve/batch``."""

    results: list[dict[str, Any]]
    summary: FhirBatchSummary


class FhirCodeableConceptResult(TypedDict):
    """Response from ``POST /v1/fhir/resolve/codeable-concept``."""

    input: dict[str, Any]
    best_match: FhirResolveResult | None
    alternatives: list[FhirResolveResult]
    unresolved: list[dict[str, Any]]


class Coding(TypedDict, total=False):
    """Lightweight FHIR ``Coding`` input type.

    Structurally compatible with ``fhir.resources.Coding`` and ``fhirpy``
    coding objects. Accepted anywhere the resolver takes a ``coding=`` input.
    """

    system: str
    code: str
    display: str
    version: str


class CodeableConcept(TypedDict, total=False):
    """Lightweight FHIR ``CodeableConcept`` input type."""

    coding: list[Coding]
    text: str


@runtime_checkable
class CodingLike(Protocol):
    """Structural protocol for any object exposing ``system`` and ``code``.

    Lets the resolver accept ``fhir.resources.Coding``, ``fhirpy`` codings,
    or any user-defined class with ``system``/``code`` attributes without
    taking a hard dependency on those libraries.
    """

    system: str | None
    code: str | None


@runtime_checkable
class CodeableConceptLike(Protocol):
    """Structural protocol for any object exposing ``coding`` and ``text``."""

    coding: list[Any] | None
    text: str | None
