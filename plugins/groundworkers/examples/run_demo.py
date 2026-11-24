"""Exercise the installed plugin through a real Groundworkers stdio MCP server."""

import argparse
import asyncio
import json
import os
import sys
import time
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent
TOOLS = {
    "compare_mappings",
    "search",
    "by_code",
    "relationships",
    "descendants",
    "fhir_resolve",
    "fhir_resolve_codeable_concept",
    "semantic_search",
    "find_similar_concepts",
}


class Client:
    def __init__(self, session, release):
        self.session = session
        self.release = release
        self.calls = 0

    async def call(self, tool, **params):
        self.calls += 1
        reply = await self.session.call_tool(f"omophub_{tool}", params)
        if reply.isError:
            raise RuntimeError(
                f"MCP call failed for {tool}: {reply.content[0].text[:250]}"
            )
        data = reply.structuredContent or json.loads(reply.content[0].text)
        if data.get("error"):
            raise RuntimeError(f"{tool}: {data.get('code')} {data.get('message')}")
        if data["vocab_release"] != self.release:
            raise ValueError("Plugin evidence belongs to a different release.")
        return data

    async def rows(self, tool, **params):
        rows = []
        page = 1
        while True:
            data = await self.call(tool, page=page, **params)
            if data.get("truncated") is True:
                raise ValueError(
                    "Hierarchy hit the API row cap; coverage is indeterminate."
                )
            meta = data["pagination"]
            if meta["page"] != page:
                raise ValueError("Unexpected pagination cursor.")
            rows.extend(data["rows"])
            if not meta["has_next"]:
                if len(rows) != meta["total_items"]:
                    raise ValueError("Incomplete result set after the final page.")
                return rows
            if not data["rows"] or page >= meta["total_pages"]:
                raise ValueError("Inconsistent next-page metadata.")
            page += 1

    async def exact(self, query, vocabulary, domain):
        rows = await self.rows(
            "search", query=query, vocabulary_id=vocabulary, domain_id=domain
        )
        matches = [
            r
            for r in rows
            if r["matched_term"]
            and r["vocabulary_id"] == vocabulary
            and r["domain_id"] == domain
            and not r["invalid_reason"]
        ]
        preferred_names = [
            r for r in matches if r["concept_name"].casefold() == query.casefold()
        ]
        matches = preferred_names or matches
        if len(matches) != 1:
            raise ValueError(f"{query!r} has {len(matches)} active exact matches.")
        return matches[0]

    async def edges(self, source, *types, reverse=False):
        return await self.rows(
            "relationships",
            concept_id=source,
            relationship_ids=list(types),
            include_reverse=reverse,
        )

    async def code(self, vocabulary, code):
        row = (await self.call("by_code", vocabulary_id=vocabulary, concept_code=code))[
            "concept"
        ]
        if (row["vocabulary_id"], row["concept_code"]) != (vocabulary, code):
            raise ValueError("Code lookup returned a different vocabulary or code.")
        return row


async def folfox(client):
    regimen = await client.exact("FOLFOX", "HemOnc", "Regimen")
    relationship = "Has cytotox chemo Rx"
    edges = await client.edges(regimen["concept_id"], relationship)
    ingredients = [
        e["target"]
        for e in edges
        if e["source"]["concept_id"] == regimen["concept_id"]
        and e["relationship_id"] == relationship
    ]
    return {
        "regimen": regimen,
        "relationship": relationship,
        "ingredients": ingredients,
    }, {
        "regimen_identity": regimen["concept_id"] == 35806596,
        "three_ingredient_ids": sorted(r["concept_id"] for r in ingredients)
        == [955632, 1318011, 1388796],
        "active_standard_rxnorm_ingredients": bool(ingredients)
        and all(
            r["vocabulary_id"] == "RxNorm"
            and r["concept_class_id"] == "Ingredient"
            and r["standard_concept"] == "S"
            and not r["invalid_reason"]
            for r in ingredients
        ),
    }


async def family_history(client):
    # The synthetic dictionary specifies family history and colorectal cancer.
    # The demo's decomposition convention assigns the finding to the value slot.
    description = "Family history of colorectal cancer"
    finding_term = description.casefold().removeprefix("family history of ")
    observation = await client.exact(
        "Family history of clinical finding", "SNOMED", "Observation"
    )
    finding = await client.exact(finding_term, "SNOMED", "Condition")
    specific = await client.exact(description, "SNOMED", "Observation")
    fields = {
        "observation_concept_id": observation["concept_id"],
        "value_as_concept_id": finding["concept_id"],
    }
    return {
        "source_field": "fhx_crc",
        "source_meaning": description,
        "proposed_fields": fields,
        "evidence": [observation, finding],
        "alternative_precoordinated_concept": specific,
        "disposition": "review",
    }, {
        "published_field_assignment": fields
        == {"observation_concept_id": 4167217, "value_as_concept_id": 37168850},
        "both_standard": observation["standard_concept"]
        == finding["standard_concept"]
        == "S",
    }


async def ascending_colon(client):
    # These are the two starting parents supplied by the published audit.
    broad = await client.rows("descendants", concept_id=443396)
    site = await client.rows("descendants", concept_id=4130997)
    if len(set(broad)) != len(broad) or len(set(site)) != len(site):
        raise ValueError(
            "Duplicate descendants across pages; cannot establish coverage."
        )
    outliers = set(site) - set(broad)
    topography = await client.code("ICDO3", "C18.2")
    topo_id = topography["concept_id"]
    site_edges = await client.edges(topo_id, "Has Topography ICDO", reverse=True)
    site_sources = {
        e["source"]["concept_id"]: e["source"]
        for e in site_edges
        if e["target"]["concept_id"] == topo_id
        and e["relationship_id"] == "Has Topography ICDO"
    }
    icdo = [r for r in site_sources.values() if r["concept_code"] == "8013/3-C18.2"]
    snomed = await client.exact(
        "Primary malignant neuroendocrine neoplasm of ascending colon",
        "SNOMED",
        "Condition",
    )
    ambiguous = await client.exact(
        "Well-differentiated neuroendocrine tumor of ascending colon",
        "SNOMED",
        "Condition",
    )
    morphology = {}
    histologies = {}
    for row in [*icdo, snomed, ambiguous]:
        edges = await client.edges(
            row["concept_id"],
            "Has asso morph",
            "Has finding site",
            "Has Histology ICDO",
            "Has Topography ICDO",
        )
        morphology[row["concept_id"]] = {
            kind: [
                e["target"]["concept_code"]
                for e in edges
                if e["relationship_id"] == kind
                and e["source"]["concept_id"] == row["concept_id"]
            ]
            for kind in sorted({e["relationship_id"] for e in edges})
        }

        for edge in edges:
            if (
                edge["relationship_id"] != "Has asso morph"
                or edge["source"]["concept_id"] != row["concept_id"]
            ):
                continue
            morph = edge["target"]
            links = await client.edges(morph["concept_id"], "Maps to", reverse=True)
            histologies[morph["concept_code"]] = sorted(
                {
                    link["source"]["concept_code"]
                    for link in links
                    if link["relationship_id"] == "Maps to"
                    and link["target"]["concept_id"] == morph["concept_id"]
                    and link["source"]["vocabulary_id"] == "ICDO3"
                }
            )
    benign_maps = {}
    for vocabulary, code in [("ICD10CM", "D3A.022"), ("ICD9CM", "209.53")]:
        source = await client.code(vocabulary, code)
        edges = await client.edges(source["concept_id"], "Maps to")
        benign_maps[code] = [
            e["target"]
            for e in edges
            if e["source"]["concept_id"] == source["concept_id"]
            and e["relationship_id"] == "Maps to"
        ]
    evidence = {
        "max_levels": 20,
        "row_cap": 5000,
        "row_cap_hit": False,
        "broad_parent": 443396,
        "broad_descendants": len(broad),
        "site_parent": 4130997,
        "site_descendants": len(site),
        "site_minus_broad_count": len(outliers),
        "topography_linked_sources": len(site_sources),
        "icdo_candidate": icdo,
        "snomed_candidate": snomed,
        "typed_edge_target_codes": morphology,
        "icdo3_codes_mapping_to_snomed_morphology": histologies,
        "ambiguous_candidate": ambiguous,
        "disposition": "manual_review",
        "benign_source_maps_to": benign_maps,
    }
    icdo_edges = morphology.get(44502762, {})
    return evidence, {
        "icdo_standard_site_outlier": [
            r["concept_id"] for r in icdo if r["standard_concept"] == "S"
        ]
        == [44502762]
        and 44502762 not in broad,
        "snomed_standard_site_outlier": snomed["concept_id"] == 761001
        and snomed["standard_concept"] == "S"
        and 761001 in outliers,
        "icdo_site_and_morphology": "C18.2" in icdo_edges.get("Has Topography ICDO", [])
        and "8013/3" in icdo_edges.get("Has Histology ICDO", [])
        and "128628002" in icdo_edges.get("Has asso morph", []),
        "snomed_site_and_morphology": "9040008"
        in morphology[snomed["concept_id"]].get("Has finding site", [])
        and bool(morphology[snomed["concept_id"]].get("Has asso morph")),
        "reverse_morphology_confirms_icdo_histology": "8013/3"
        in histologies.get("128628002", []),
        "published_benign_source_target": ambiguous["concept_id"] == 1077457
        and all(
            any(r["concept_id"] == ambiguous["concept_id"] for r in targets)
            for targets in benign_maps.values()
        ),
    }


async def fhir_coding(client):
    params = {
        "system": "http://hl7.org/fhir/sid/icd-10-cm",
        "code": "E11.9",
        "resource_type": "Condition",
        "include_quality": True,
    }
    row = (await client.call("fhir_resolve", **params))["data"]["resolution"]
    unknown = (
        await client.call(
            "fhir_resolve",
            system=params["system"],
            code="DEMO-NO-MATCH",
            on_unmapped="sentinel",
        )
    )["data"]["resolution"]
    return {
        "input": params,
        "resolution": row,
        "unknown_standard_id": unknown["standard_concept"]["concept_id"],
    }, {
        "source_and_target": row["source_concept"]["concept_id"] == 35206882
        and row["standard_concept"]["concept_id"] == 201826,
        "cdm_table": row["target_table"] == "condition_occurrence",
        "unmapped_sentinel": unknown["standard_concept"]["concept_id"] == 0,
    }


async def fhir_codeable_concept(client):
    coding = [
        {"system": "http://snomed.info/sct", "code": "44054006"},
        {
            "system": "http://hl7.org/fhir/sid/icd-10-cm",
            "code": "E11.9",
            "user_selected": True,
        },
        {"system": "http://snomed.info/sct", "code": "999999999999999999"},
    ]
    data = (
        await client.call(
            "fhir_resolve_codeable_concept", coding=coding, resource_type="Condition"
        )
    )["data"]
    return data, {
        "selected_source": data["best_match"]["input"]["code"] == "E11.9",
        "standard_target": data["best_match"]["resolution"]["standard_concept"][
            "concept_id"
        ]
        == 201826,
        "snomed_alternative": any(
            r["input"]["code"] == "44054006" for r in data["alternatives"]
        ),
        "unresolved_coding": any(
            r["input"]["code"] == coding[-1]["code"] for r in data["unresolved"]
        ),
    }


async def hosted_semantic(client):
    rows = (
        await client.call(
            "semantic_search",
            query="heart attack",
            vocabulary_ids="SNOMED",
            domain_ids="Condition",
            standard_concept="S",
            page_size=5,
        )
    )["data"]["results"]
    return {"query": "heart attack", "results": rows}, {
        "contains_myocardial_infarction": any(
            row["concept_id"] == 4329847 for row in rows
        ),
        "filtered_scored_results": bool(rows)
        and all(
            row["vocabulary_id"] == "SNOMED"
            and row["domain_id"] == "Condition"
            and row["standard_concept"] == "S"
            and 0.5 <= row["similarity_score"] <= 1
            for row in rows
        ),
    }


async def hosted_similarity(client):
    data = (
        await client.call(
            "find_similar_concepts",
            concept_id=201826,
            algorithm="hybrid",
            vocabulary_ids="SNOMED",
            domain_ids="Condition",
            similarity_threshold=0.3,
            page_size=3,
            include_explanations=True,
        )
    )["data"]
    rows = data["similar_concepts"]
    return data, {
        "hybrid_executed": data["search_metadata"]["algorithm_used"] == "hybrid",
        "ranked_neighbors": bool(rows)
        and all(
            row["concept_id"] != 201826
            and row["vocabulary_id"] == "SNOMED"
            and row["domain_id"] == "Condition"
            and row["similarity_score"] >= 0.3
            for row in rows
        ),
    }


async def mapping_release_comparison(client):
    evidence = await client.call(
        "compare_mappings",
        vocabulary_id="ICD10CM",
        concept_code="D3A.022",
        baseline_release="2024.2",
    )
    return evidence, {
        "baseline_verified": evidence["baseline"]["vocab_release"] == "2024.2",
        "current_verified": evidence["current"]["vocab_release"] == "2026.2",
        "added_edges": evidence["added"]
        == [
            {"relationship_id": "Maps to", "target_concept_id": i}
            for i in (1244590, 1345982)
        ],
        "removed_edge": evidence["removed"]
        == [{"relationship_id": "Maps to", "target_concept_id": 760937}],
    }


async def run(release, suite):
    if not os.environ.get("OMOPHUB_API_KEY"):
        raise ValueError("Set OMOPHUB_API_KEY before running the live checks.")
    child_env = {
        "OMOPHUB_API_KEY": os.environ["OMOPHUB_API_KEY"],
        "OMOPHUB_VOCAB_RELEASE": release,
    }
    if "PYSTOW_HOME" in os.environ:
        child_env["PYSTOW_HOME"] = os.environ["PYSTOW_HOME"]
    params = StdioServerParameters(
        command=str(Path(sys.executable).with_name("groundworkers")),
        args=["--config-path", str(ROOT / "demo.toml"), "--transport", "stdio"],
        env=child_env,
    )
    report = {
        "vocab_release": release,
        "groundworkers_version": version("groundworkers"),
        "adapter_version": version("groundworkers-omophub"),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "cases": {},
    }
    async with (
        stdio_client(params) as (read, write),
        ClientSession(read, write) as session,
    ):
        await session.initialize()
        names = {tool.name for tool in (await session.list_tools()).tools}
        report["plugin_tools"] = sorted("omophub_" + name for name in TOOLS)
        if not set(report["plugin_tools"]).issubset(names):
            raise RuntimeError(
                f"Groundworkers is missing plugin tools: {sorted(set(report['plugin_tools']) - names)}"
            )
        client = Client(session, release)
        cases = (
            (folfox, family_history, ascending_colon)
            if suite == "groundworkers"
            else (
                mapping_release_comparison,
                fhir_coding,
                fhir_codeable_concept,
                hosted_semantic,
                hosted_similarity,
            )
        )
        for case in cases:
            start, before = time.monotonic(), client.calls
            try:
                evidence, checks = await case(client)
                result = {
                    "status": "match" if all(checks.values()) else "difference",
                    "checks": checks,
                    "evidence": evidence,
                }
            except (ValueError, RuntimeError, KeyError) as exc:
                result = {"status": "error", "error": str(exc)}
            result.update(
                api_tool_calls=client.calls - before,
                elapsed_seconds=round(time.monotonic() - start, 2),
            )
            report["cases"][case.__name__] = result
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--release", required=True, help="Explicit OMOPHub release, e.g. 2026.2"
    )
    parser.add_argument(
        "--suite", choices=["groundworkers", "omophub"], default="groundworkers"
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = asyncio.run(run(args.release, args.suite))
    output = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(output)
    else:
        print(output, end="")
    statuses = [c["status"] for c in report["cases"].values()]
    sys.exit(2 if "error" in statuses else int("difference" in statuses))
