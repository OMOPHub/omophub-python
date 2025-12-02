"""Hierarchy type definitions."""

from __future__ import annotations

from typing import Any, TypedDict

from typing_extensions import NotRequired


class HierarchyConcept(TypedDict):
    """Base type for concepts in hierarchy (ancestors and descendants)."""

    concept_id: int
    concept_name: str
    vocabulary_id: str
    concept_code: str
    domain_id: NotRequired[str]
    concept_class_id: NotRequired[str]
    standard_concept: NotRequired[str | None]
    level: NotRequired[int]
    min_levels_of_separation: NotRequired[int]
    max_levels_of_separation: NotRequired[int]


# Ancestor and Descendant are aliases for HierarchyConcept
# They share identical structure but different semantic meaning
Ancestor = HierarchyConcept
"""Ancestor concept in hierarchy (alias for HierarchyConcept)."""

Descendant = HierarchyConcept
"""Descendant concept in hierarchy (alias for HierarchyConcept)."""


class HierarchyPath(TypedDict):
    """Path in concept hierarchy."""

    path: list[int]
    concepts: NotRequired[list[dict[str, Any]]]
    length: NotRequired[int]


class HierarchySummary(TypedDict, total=False):
    """Summary of hierarchy query results."""

    total_ancestors: int
    total_descendants: int
    max_hierarchy_depth: int
    unique_vocabularies: list[str]
    relationship_types_used: list[str]
    classification_count: int
