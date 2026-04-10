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


class DomainDistribution(TypedDict):
    """Domain distribution within vocabulary statistics."""

    domain_id: str
    domain_name: str
    concept_count: int


class VocabularyStats(TypedDict):
    """Vocabulary statistics from /vocabularies/{vocabulary_id}/stats endpoint."""

    vocabulary_id: str
    vocabulary_name: str
    total_concepts: int
    standard_concepts: NotRequired[int]
    classification_concepts: NotRequired[int]
    invalid_concepts: NotRequired[int]
    active_concepts: NotRequired[int]
    valid_start_date: NotRequired[str]
    valid_end_date: NotRequired[str]
    last_updated: NotRequired[str]
    domain_distribution: NotRequired[list[DomainDistribution]]


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
