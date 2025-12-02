"""Vocabulary type definitions."""

from __future__ import annotations

from typing import TypedDict

from typing_extensions import NotRequired


class VocabularySummary(TypedDict):
    """Minimal vocabulary information for listings."""

    vocabulary_id: str
    vocabulary_name: str
    vocabulary_version: NotRequired[str]


class VocabularyDomain(TypedDict):
    """Domain statistics within a vocabulary."""

    domain_id: str
    concept_count: int
    standard_count: NotRequired[int]
    classification_count: NotRequired[int]


class VocabularyStats(TypedDict):
    """Vocabulary statistics."""

    total_concepts: int
    standard_concepts: NotRequired[int]
    classification_concepts: NotRequired[int]
    invalid_concepts: NotRequired[int]
    relationships_count: NotRequired[int]
    synonyms_count: NotRequired[int]


class Vocabulary(TypedDict):
    """Full vocabulary information."""

    vocabulary_id: str
    vocabulary_name: str
    vocabulary_reference: NotRequired[str]
    vocabulary_version: NotRequired[str]
    vocabulary_concept_id: NotRequired[int]
    # Extended fields
    concept_count: NotRequired[int]
    domains: NotRequired[list[VocabularyDomain]]
    last_updated: NotRequired[str]
    statistics: NotRequired[VocabularyStats]
