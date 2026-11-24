"""Read-only OMOPHub vocabulary tools for Groundworkers."""

import os
import re
import time
from typing import Annotated, Literal
from urllib.parse import quote

import httpx
from groundworkers.base.errors import GroundworkersError
from pydantic import AliasChoices, BaseModel, ConfigDict, Field

CONCEPT_FIELDS = (
    "concept_id",
    "concept_name",
    "concept_code",
    "vocabulary_id",
    "domain_id",
    "concept_class_id",
    "standard_concept",
    "invalid_reason",
)


# Same chart-label and whole-resource checks as the OMOPHub MCP terminology tools.
RECORD_FIELDS = re.compile(
    r"""\b(?:MRN|medical[ _]?record[ _]?number|patient[ _]?(?:name|id)|date[ _]?of[ _]?birth|birthDate|DOB)["']?\s*[:=#]|["']resourceType["']\s*:\s*["'](?!(?:Coding|CodeableConcept)["'])[a-z][a-z0-9]*["']""",
    re.IGNORECASE,
)


def check_terminology_input(value):
    if isinstance(value, str):
        if RECORD_FIELDS.search(value):
            raise ValueError("Provide only a terminology code or a de-identified term.")
    elif isinstance(value, dict):
        for item in value.values():
            check_terminology_input(item)
    elif isinstance(value, list):
        for item in value:
            check_terminology_input(item)


class Coding(BaseModel):
    model_config = ConfigDict(extra="forbid")
    system: Annotated[str, Field(min_length=1, max_length=512)]
    code: Annotated[str, Field(min_length=1, max_length=128)]
    display: Annotated[str, Field(max_length=500)] | None = None
    user_selected: bool | None = Field(
        default=None, validation_alias=AliasChoices("user_selected", "userSelected")
    )


def concept(row):
    return {field: row[field] for field in CONCEPT_FIELDS}


class Vocabulary:
    def __init__(self, key, release):
        if not re.fullmatch(r"[0-9]{4}\.[0-9]+", release):
            raise ValueError(
                "Set an explicit numeric OMOPHUB_VOCAB_RELEASE such as 2026.2."
            )
        self.release = release
        self._api_key = key

    def read(self, path, *, body=None, **params):
        params = {k: v for k, v in params.items() if v is not None}
        if body is not None:
            body = {k: v for k, v in body.items() if v is not None}
        check_terminology_input([params, body])
        params["vocab_release"] = self.release
        url = f"https://api.omophub.com/v1/{path}"
        for attempt in range(3):
            try:
                response = httpx.request(
                    "GET" if body is None else "POST",
                    url,
                    json=body,
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "X-Vocab-Release": self.release,
                    },
                    params=params,
                    timeout=30,
                    follow_redirects=False,
                )
            except httpx.RequestError:
                raise GroundworkersError(
                    "BACKEND_UNAVAIL", "Could not reach the OMOPHub API."
                ) from None
            if response.status_code != 429:
                break
            delay = response.headers.get("Retry-After", "60")
            if attempt == 2 or not delay.isdecimal() or int(delay) > 65:
                raise GroundworkersError(
                    "BACKEND_UNAVAIL", "OMOPHub rate limit reached; retry later."
                )
            time.sleep(int(delay) + 1)
        if response.status_code in (400, 422):
            raise ValueError("OMOPHub rejected the terminology input.")
        if response.status_code in (401, 403):
            raise GroundworkersError(
                "BACKEND_UNAVAIL",
                f"OMOPHub denied access (HTTP {response.status_code}). Check the key and its vocabulary access.",
            )
        if response.status_code == 404:
            raise GroundworkersError(
                "NOT_FOUND",
                f"OMOPHub could not find the requested release or record on {self.release}.",
            )
        if response.status_code != 200:
            raise GroundworkersError(
                "BACKEND_UNAVAIL", f"OMOPHub returned HTTP {response.status_code}."
            )
        payload = response.json()
        if response.headers.get("X-Vocab-Release") != self.release:
            raise ValueError(
                "OMOPHub did not confirm the requested release in the response header."
            )
        reported = payload["meta"].get("vocab_release")
        if reported is not None and reported != self.release:
            raise ValueError("OMOPHub returned conflicting release metadata.")
        return payload

    def page(self, payload, rows):
        pagination = payload["meta"]["pagination"]
        return {"vocab_release": self.release, "rows": rows, "pagination": pagination}

    def _mapping_snapshot(self, vocabulary_id: str, concept_code: str) -> dict:
        source = self.by_code(vocabulary_id, concept_code)["concept"]
        source_id = source["concept_id"]
        targets = set()
        expected_total = None
        page = 1
        while True:
            response = self.relationships(
                source_id, ["Maps to", "Maps to value"], page=page
            )
            meta = response["pagination"]
            if expected_total is None:
                expected_total = meta["total_items"]
            if meta["page"] != page or meta["total_items"] != expected_total:
                raise ValueError(
                    "Inconsistent mapping pagination across a pinned release."
                )
            for edge in response["rows"]:
                if edge["source"]["concept_id"] != source_id or edge[
                    "relationship_id"
                ] not in ("Maps to", "Maps to value"):
                    raise ValueError(
                        "Unexpected direction or relationship type in mapping evidence."
                    )
                targets.add((edge["relationship_id"], edge["target"]["concept_id"]))
            if not meta["has_next"]:
                break
            if not response["rows"] or page >= meta["total_pages"]:
                raise ValueError("Incomplete mapping pagination.")
            page += 1
        if len(targets) != expected_total:
            raise ValueError("Incomplete or duplicate mapping evidence.")
        return {
            "vocab_release": self.release,
            "source_concept": source,
            "edges": sorted(targets),
        }

    def compare_mappings(
        self, vocabulary_id: str, concept_code: str, baseline_release: str
    ) -> dict:
        """Compare active outgoing Maps to and Maps to value edges from a baseline release to the configured release. Both hosted snapshots are verified independently."""
        if baseline_release == self.release:
            raise ValueError("Choose a baseline different from the configured release.")
        baseline = Vocabulary(self._api_key, baseline_release)._mapping_snapshot(
            vocabulary_id, concept_code
        )
        current = self._mapping_snapshot(vocabulary_id, concept_code)
        before, after = set(baseline["edges"]), set(current["edges"])

        def records(edges):
            return [
                {"relationship_id": kind, "target_concept_id": target}
                for kind, target in sorted(edges)
            ]

        return {
            "vocab_release": self.release,
            "baseline": {**baseline, "edges": records(before)},
            "current": {**current, "edges": records(after)},
            "added": records(after - before),
            "removed": records(before - after),
        }

    def search(
        self, query: str, vocabulary_id: str, domain_id: str, page: int = 1
    ) -> dict:
        """Find active exact name, synonym or code matches in one vocabulary and domain."""
        payload = self.read(
            "search/concepts",
            query=query,
            vocabulary_ids=vocabulary_id,
            domain_ids=domain_id,
            exact_match=True,
            include_synonyms=True,
            include_invalid=False,
            page=page,
            page_size=100,
        )
        rows = []
        for row in payload["data"]:
            match = next(
                (
                    term
                    for term in (row["concept_name"], *row.get("synonyms", []))
                    if term.casefold() == query.strip().casefold()
                ),
                None,
            )
            rows.append({**concept(row), "matched_term": match})
        return self.page(payload, rows)

    def by_code(self, vocabulary_id: str, concept_code: str) -> dict:
        """Look up a concept using its vocabulary and code."""
        path = f"concepts/by-code/{quote(vocabulary_id, safe='')}/{quote(concept_code, safe='')}"
        return {
            "vocab_release": self.release,
            "concept": concept(self.read(path)["data"]),
        }

    def relationships(
        self,
        concept_id: int,
        relationship_ids: list[str],
        include_reverse: bool = False,
        page: int = 1,
    ) -> dict:
        """Page through active, typed edges with their original direction."""
        if concept_id < 1 or not relationship_ids or not all(relationship_ids):
            raise ValueError(
                "Supply a positive concept ID and at least one relationship type."
            )
        payload = self.read(
            f"concepts/{concept_id}/relationships",
            relationship_ids=",".join(relationship_ids),
            include_invalid=False,
            include_reverse=include_reverse,
            page=page,
            page_size=200,
        )
        rows = [
            {
                "relationship_id": r["relationship_id"],
                "source": concept(r["concept_1"]),
                "target": concept(r["concept_2"]),
            }
            for r in payload["data"]["relationships"]
        ]
        return self.page(payload, rows)

    def descendants(self, concept_id: int, page: int = 1) -> dict:
        """Page through active descendants within 20 levels and the 5000-row API cap."""
        if concept_id < 1:
            raise ValueError("Supply a positive ancestor concept ID.")
        payload = self.read(
            f"concepts/{concept_id}/descendants",
            max_levels=20,
            max_results=5000,
            include_invalid=False,
            page=page,
            page_size=200,
        )
        data = payload["data"]
        result = self.page(payload, [r["concept_id"] for r in data["descendants"]])
        result.update(max_levels=20, truncated=data["hierarchy_summary"]["truncated"])
        return result

    def result(self, path, *, body=None, **params):
        response = self.read(path, body=body, **params)
        return {
            "vocab_release": self.release,
            "data": response["data"],
            "meta": response["meta"],
        }

    def fhir_resolve(
        self,
        system: str | None = None,
        code: str | None = None,
        display: str | None = None,
        vocabulary_id: str | None = None,
        resource_type: str | None = None,
        include_quality: bool = False,
        include_recommendations: bool = False,
        on_unmapped: Literal["error", "sentinel"] = "error",
    ) -> dict:
        """Resolve one terminology Coding to its source, standard target and CDM table. Concept ID 0 means unmapped."""
        if not (code and (system or vocabulary_id)) and not display:
            raise ValueError(
                "Provide a system and code, vocabulary_id and code, or a display term."
            )
        return self.result(
            "fhir/resolve",
            body={
                "system": system,
                "code": code,
                "display": display,
                "vocabulary_id": vocabulary_id,
                "resource_type": resource_type,
                "include_quality": include_quality,
                "include_recommendations": include_recommendations,
                "on_unmapped": on_unmapped,
            },
        )

    def fhir_resolve_codeable_concept(
        self,
        coding: Annotated[list[Coding], Field(max_length=20)],
        text: str | None = None,
        resource_type: str | None = None,
        include_quality: bool = False,
        include_recommendations: bool = False,
        on_unmapped: Literal["error", "sentinel"] = "error",
    ) -> dict:
        """Resolve codings for one clinical idea, retaining the best match, alternatives and unresolved codings. Use coding=[] for text alone."""
        if not coding and not text:
            raise ValueError("Provide codings or a terminology text.")
        return self.result(
            "fhir/resolve/codeable-concept",
            body={
                "coding": [entry.model_dump(exclude_none=True) for entry in coding],
                "text": text,
                "resource_type": resource_type,
                "include_quality": include_quality,
                "include_recommendations": include_recommendations,
                "on_unmapped": on_unmapped,
            },
        )

    def semantic_search(
        self,
        query: Annotated[str, Field(min_length=1, max_length=500)],
        vocabulary_ids: str | None = None,
        domain_ids: str | None = None,
        standard_concept: Literal["S", "C"] | None = None,
        threshold: Annotated[float, Field(ge=0, le=1)] = 0.5,
        page_size: Annotated[int, Field(ge=1, le=100)] = 10,
    ) -> dict:
        """Rank a terminology phrase using OMOPHub's hosted embeddings. Filters accept comma-separated IDs."""
        return self.result(
            "search/semantic",
            query=query,
            vocabulary_ids=vocabulary_ids,
            domain_ids=domain_ids,
            standard_concept=standard_concept,
            threshold=threshold,
            page_size=page_size,
        )

    def find_similar_concepts(
        self,
        concept_id: int | None = None,
        concept_name: str | None = None,
        query: str | None = None,
        algorithm: Literal["semantic", "lexical", "hybrid"] = "semantic",
        similarity_threshold: Annotated[float, Field(ge=0, le=1)] = 0.7,
        vocabulary_ids: str | None = None,
        domain_ids: str | None = None,
        concept_class_ids: str | None = None,
        page: Annotated[int, Field(ge=1)] = 1,
        page_size: Annotated[int, Field(ge=1, le=1000)] = 20,
        include_explanations: bool = False,
    ) -> dict:
        """Find ranked neighbours for one concept ID, name or term. Returns scores and the algorithm actually used."""
        if sum(item is not None for item in (concept_id, concept_name, query)) != 1:
            raise ValueError("Supply exactly one of concept_id, concept_name or query.")
        body = {
            "concept_id": concept_id,
            "concept_name": concept_name,
            "query": query,
            "algorithm": algorithm,
            "similarity_threshold": similarity_threshold,
            "page": page,
            "page_size": page_size,
            "include_explanations": include_explanations,
        }
        for key, value in (
            ("vocabulary_ids", vocabulary_ids),
            ("domain_ids", domain_ids),
            ("concept_class_ids", concept_class_ids),
        ):
            if value:
                body[key] = [part.strip() for part in value.split(",") if part.strip()]
        return self.result("search/similar", body=body)


class OMOPHubPlugin:
    name = "omophub"
    config_cls = None

    def build(self, context, config):
        key = os.environ.get("OMOPHUB_API_KEY")
        release = os.environ.get("OMOPHUB_VOCAB_RELEASE")
        return Vocabulary(key, release) if key and release else None

    def register(self, server, state):
        for method in (
            state.compare_mappings,
            state.search,
            state.by_code,
            state.relationships,
            state.descendants,
            state.fhir_resolve,
            state.fhir_resolve_codeable_concept,
            state.semantic_search,
            state.find_similar_concepts,
        ):
            server.tool(f"omophub_{method.__name__}")(method)


plugin = OMOPHubPlugin()
