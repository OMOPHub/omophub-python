"""Mapping type definitions."""

from __future__ import annotations

from typing import TypedDict

from typing_extensions import NotRequired


class MappingQuality(TypedDict, total=False):
    """Quality assessment for a mapping."""

    confidence_score: float
    equivalence_type: str
    semantic_similarity: float
    mapping_source: str
    validation_status: str
    last_reviewed_date: str


class MappingContext(TypedDict, total=False):
    """Context information for a mapping."""

    use_case: str
    geographic_scope: str
    temporal_scope: str
    mapping_notes: str
    cross_walk_source: str


class Mapping(TypedDict):
    """Concept mapping to another vocabulary.

    The optional fields are optional because this type is shared by two
    endpoints that populate different subsets -- not because the server
    decides case by case:

    - ``mappings.get`` (``GET /concepts/{id}/mappings``) returns exactly
      ``source_concept_id``, ``source_concept_name``, ``target_concept_id``,
      ``target_concept_name``, ``relationship_id`` and ``confidence``.
      Supplying ``target_vocabulary`` does NOT add the vocabulary/code fields
      -- measured against production 2026-08-12. Resolve a target's vocabulary
      and code with ``concepts.get(target_concept_id)``.
    - ``mappings.map`` (``POST /mappings/map``) additionally returns the
      ``source_*`` / ``target_*`` ``vocabulary_id`` and ``concept_code``.

    Note: Confidence score should be accessed via `quality.confidence_score`
    when include_mapping_quality=True is requested.
    """

    source_concept_id: int
    source_concept_name: NotRequired[str]
    source_vocabulary_id: NotRequired[str]
    source_concept_code: NotRequired[str]
    target_concept_id: int
    target_concept_name: NotRequired[str]
    target_vocabulary_id: NotRequired[str]
    target_concept_code: NotRequired[str]
    target_domain_id: NotRequired[str]
    target_concept_class_id: NotRequired[str]
    target_standard_concept: NotRequired[str | None]
    mapping_type: NotRequired[str]
    relationship_id: NotRequired[str]
    quality: NotRequired[MappingQuality]
    context: NotRequired[MappingContext]


class MappingSummary(TypedDict, total=False):
    """Summary of mapping query results."""

    total_mappings: int
    direct_mappings: int
    indirect_mappings: int
    target_vocabularies: list[str]
    coverage_percentage: float
    average_confidence: float
