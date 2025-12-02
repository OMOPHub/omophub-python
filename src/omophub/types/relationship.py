"""Relationship type definitions."""

from __future__ import annotations

from typing import Any, TypedDict

from typing_extensions import NotRequired


class Relationship(TypedDict):
    """Concept relationship."""

    relationship_id: str
    relationship_name: NotRequired[str]
    direction: NotRequired[str]  # "outbound" or "inbound"
    target_concept_id: int
    target_concept_name: NotRequired[str]
    target_vocabulary_id: NotRequired[str]
    target_concept_code: NotRequired[str]
    target_domain_id: NotRequired[str]
    target_concept_class_id: NotRequired[str]
    target_standard_concept: NotRequired[str | None]
    valid_start_date: NotRequired[str]
    valid_end_date: NotRequired[str]
    invalid_reason: NotRequired[str | None]


class RelationshipType(TypedDict):
    """Relationship type metadata."""

    relationship_id: str
    relationship_name: str
    is_hierarchical: NotRequired[bool]
    is_defining: NotRequired[bool]
    is_symmetric: NotRequired[bool]
    is_transitive: NotRequired[bool]
    reverse_relationship_id: NotRequired[str]
    relationship_concept_id: NotRequired[int]
    category: NotRequired[str]
    primary_vocabularies: NotRequired[list[str]]
    usage_count: NotRequired[int]
    example_concepts: NotRequired[list[dict[str, Any]]]


class RelationshipSummary(TypedDict, total=False):
    """Summary of relationship query results."""

    total_relationships: int
    outbound_count: int
    inbound_count: int
    relationship_types: list[str]
    target_vocabularies: list[str]
