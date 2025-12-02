"""Concept type definitions."""

from __future__ import annotations

from typing import Any, TypedDict

from typing_extensions import NotRequired


class Synonym(TypedDict):
    """Concept synonym information."""

    concept_synonym_name: str
    language_concept_id: NotRequired[int]


class ConceptSummary(TypedDict):
    """Minimal concept information for listings."""

    concept_id: int
    concept_name: str
    vocabulary_id: str
    concept_code: str


class Concept(TypedDict):
    """Full concept information."""

    concept_id: int
    concept_name: str
    domain_id: str
    vocabulary_id: str
    concept_class_id: str
    standard_concept: str | None
    concept_code: str
    valid_start_date: str
    valid_end_date: str
    invalid_reason: NotRequired[str | None]
    # Optional extended fields
    synonyms: NotRequired[list[Synonym]]
    relationships: NotRequired[list[dict[str, Any]]]


class RelatedConcept(TypedDict):
    """Related concept with relatedness information."""

    concept_id: int
    concept_name: str
    vocabulary_id: str
    concept_code: str
    domain_id: str
    concept_class_id: str
    standard_concept: str | None
    relatedness_score: NotRequired[float]
    relatedness_type: NotRequired[str]
    hierarchical_score: NotRequired[float]
    semantic_score: NotRequired[float]
    co_occurrence_score: NotRequired[float]
    mapping_score: NotRequired[float]
    explanation: NotRequired[str]


class BatchConceptResult(TypedDict):
    """Result from batch concept retrieval."""

    concepts: list[Concept]
    failed_concepts: NotRequired[list[int]]
    summary: NotRequired[dict[str, Any]]
