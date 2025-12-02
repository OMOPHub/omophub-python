"""Domain type definitions."""

from __future__ import annotations

from typing import Any, TypedDict

from typing_extensions import NotRequired


class DomainCategory(TypedDict):
    """Domain category classification."""

    category: str  # clinical, administrative, derived, metadata
    description: NotRequired[str]


class DomainStats(TypedDict, total=False):
    """Domain statistics."""

    total_concepts: int
    standard_concepts: int
    classification_concepts: int
    vocabulary_distribution: dict[str, int]
    concept_class_distribution: dict[str, int]
    growth_trend: float
    usage_frequency: int
    relationship_density: float


class DomainSummary(TypedDict):
    """Minimal domain information for listings."""

    domain_id: str
    domain_name: str
    concept_count: NotRequired[int]


class Domain(TypedDict):
    """Full domain information."""

    domain_id: str
    domain_name: str
    domain_concept_id: NotRequired[int]
    category: NotRequired[DomainCategory]
    concept_count: NotRequired[int]
    statistics: NotRequired[DomainStats]
    example_concepts: NotRequired[list[dict[str, Any]]]
